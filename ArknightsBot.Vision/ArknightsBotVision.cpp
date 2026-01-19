#include <iostream>

// Định nghĩa macro để xuất hàm ra DLL
#define EXPORT extern "C" __declspec(dllexport)

// Hàm test: Cộng 2 số nguyên
EXPORT int Sum(int a, int b) {
    return a + b;
}

// Hàm test: Trả về một số nhận diện (ví dụ)
EXPORT double FindImageMock() {
    return 0.95; // Giả lập độ chính xác 95%
}