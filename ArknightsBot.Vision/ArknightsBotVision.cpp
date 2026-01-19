#include <opencv2/opencv.hpp>
#include <vector>

#define EXPORT extern "C" __declspec(dllexport)

// Hàm cũ (giữ lại nếu cần)
EXPORT bool FindImage(const char* screenPath, const char* templatePath, int* outX, int* outY, double* outSim) {
    try {
        cv::Mat imgScreen = cv::imread(screenPath);
        cv::Mat imgTemplate = cv::imread(templatePath);
        if (imgScreen.empty() || imgTemplate.empty()) return false;

        cv::Mat result;
        int result_cols = imgScreen.cols - imgTemplate.cols + 1;
        int result_rows = imgScreen.rows - imgTemplate.rows + 1;
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

// --- HÀM MỚI: ĐỌC TỪ RAM (Siêu nhanh) ---
// screenData: Con trỏ trỏ tới dữ liệu ảnh trong RAM
// dataLen: Độ dài dữ liệu
EXPORT bool FindImageFromMemory(unsigned char* screenData, int dataLen, const char* templatePath, int* outX, int* outY, double* outSim) {
    try {
        // 1. Decode ảnh từ RAM (thay vì đọc file)
        std::vector<unsigned char> data(screenData, screenData + dataLen);
        cv::Mat imgScreen = cv::imdecode(data, cv::IMREAD_COLOR);

        // 2. Đọc ảnh mẫu (Ảnh mẫu thì đọc file được vì nó nhỏ và cache được, hoặc tối ưu sau)
        cv::Mat imgTemplate = cv::imread(templatePath);

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