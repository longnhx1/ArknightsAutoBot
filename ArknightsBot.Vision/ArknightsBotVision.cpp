#include <opencv2/opencv.hpp>
#include <iostream>

#define EXPORT extern "C" __declspec(dllexport)

// Hàm cộng để test kết nối (Giữ lại)
EXPORT int Sum(int a, int b) {
    return a + b;
}

// HÀM MỚI: Tìm vị trí ảnh mẫu trong ảnh màn hình
// Trả về: true nếu tìm thấy, false nếu không
// outX, outY: Tọa độ tìm thấy
// outSim: Độ tương đồng (0.0 đến 1.0)
EXPORT bool FindImage(const char* screenPath, const char* templatePath, int* outX, int* outY, double* outSim) {
    try {
        // 1. Đọc ảnh từ đường dẫn
        cv::Mat imgScreen = cv::imread(screenPath);
        cv::Mat imgTemplate = cv::imread(templatePath);

        // Kiểm tra ảnh có lỗi không
        if (imgScreen.empty() || imgTemplate.empty()) {
            return false;
        }

        // 2. Tạo kết quả chứa độ tương đồng
        int result_cols = imgScreen.cols - imgTemplate.cols + 1;
        int result_rows = imgScreen.rows - imgTemplate.rows + 1;

        if (result_cols <= 0 || result_rows <= 0) return false; // Ảnh mẫu to hơn màn hình thì lỗi

        cv::Mat result;
        result.create(result_rows, result_cols, CV_32FC1);

        // 3. So khớp (Template Matching)
        // TM_CCOEFF_NORMED là thuật toán chuẩn nhất (1.0 là giống hệt)
        cv::matchTemplate(imgScreen, imgTemplate, result, cv::TM_CCOEFF_NORMED);

        // 4. Tìm vị trí có độ tương đồng cao nhất (Max Loc)
        double minVal, maxVal;
        cv::Point minLoc, maxLoc;
        cv::minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc);

        // 5. Gán kết quả ra ngoài
        *outSim = maxVal;

        // Tính tọa độ tâm của ảnh tìm được (thay vì góc trái trên)
        *outX = maxLoc.x + (imgTemplate.cols / 2);
        *outY = maxLoc.y + (imgTemplate.rows / 2);

        return true;
    }
    catch (...) {
        return false;
    }
}