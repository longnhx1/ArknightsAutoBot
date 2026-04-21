#include <opencv2/opencv.hpp>
#include <vector>
#include <unordered_map>
#include <string>

#define EXPORT extern "C" __declspec(dllexport)

// --- TỐI ƯU HÓA: BỘ ĐỆM CACHE TRÊN RAM ---
std::unordered_map<std::string, cv::Mat> templateCache;

// Hàm cũ (giữ lại nếu cần)
EXPORT bool FindImage(const char* screenPath, const char* templatePath, int* outX, int* outY, double* outSim) {
    try {
        cv::Mat imgScreen = cv::imread(screenPath);
        std::string tPath(templatePath);
        cv::Mat imgTemplate;
        
        if (templateCache.find(tPath) != templateCache.end()) {
            imgTemplate = templateCache[tPath];
        } else {
            imgTemplate = cv::imread(templatePath);
            if (!imgTemplate.empty()) templateCache[tPath] = imgTemplate;
        }

        if (imgScreen.empty() || imgTemplate.empty()) return false;

        cv::Mat result;
        int result_cols = imgScreen.cols - imgTemplate.cols + 1;
        int result_rows = imgScreen.rows - imgTemplate.rows + 1;
        if (result_rows <= 0 || result_cols <= 0) return false;

        result.create(result_rows, result_cols, CV_32FC1);
        cv::matchTemplate(imgScreen, imgTemplate, result, cv::TM_CCOEFF_NORMED);

        double minVal, maxVal;
        cv::Point minLoc, maxLoc;
        cv::minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc);

        *outSim = maxVal;
        *outX = maxLoc.x + (imgTemplate.cols / 2);
        *outY = maxLoc.y + (imgTemplate.rows / 2);
        return true;
    }
    catch (...) { return false; }
}

// --- HÀM MỚI: ĐỌC TỪ RAM (Siêu nhanh & Đã tối ưu) ---
// screenData: Con trỏ trỏ tới dữ liệu ảnh trong RAM
// dataLen: Độ dài dữ liệu
EXPORT bool FindImageFromMemory(unsigned char* screenData, int dataLen, const char* templatePath, int* outX, int* outY, double* outSim) {
    try {
        // 1. Decode ảnh từ RAM (thay vì đọc file)
        std::vector<unsigned char> data(screenData, screenData + dataLen);
        cv::Mat imgScreen = cv::imdecode(data, cv::IMREAD_COLOR);

        // 2. Đọc ảnh mẫu (Dùng Cache để tối ưu hóa - CHỈ ĐỌC Ổ CỨNG 1 LẦN)
        std::string tPath(templatePath);
        cv::Mat imgTemplate;
        
        if (templateCache.find(tPath) != templateCache.end()) {
            imgTemplate = templateCache[tPath]; // Lấy từ RAM
        } else {
            imgTemplate = cv::imread(templatePath); // Đọc ổ cứng lần đầu
            if (!imgTemplate.empty()) {
                templateCache[tPath] = imgTemplate; // Lưu vào RAM cho các lần sau
            }
        }

        if (imgScreen.empty() || imgTemplate.empty()) return false;

        // 3. Xử lý như cũ
        cv::Mat result;
        int result_cols = imgScreen.cols - imgTemplate.cols + 1;
        int result_rows = imgScreen.rows - imgTemplate.rows + 1;
        if (result_rows <= 0 || result_cols <= 0) return false;

        result.create(result_rows, result_cols, CV_32FC1);
        cv::matchTemplate(imgScreen, imgTemplate, result, cv::TM_CCOEFF_NORMED);

        double minVal, maxVal;
        cv::Point minLoc, maxLoc;
        cv::minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc);

        *outSim = maxVal;
        *outX = maxLoc.x + (imgTemplate.cols / 2);
        *outY = maxLoc.y + (imgTemplate.rows / 2);

        return true;
    }
    catch (...) { return false; }
}