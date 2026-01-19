import sys
import os
import ctypes

def main():
    # 1. Xác định vị trí file DLL
    # Script đang ở: src/Logic/main.py
    # DLL đang ở:    bin/ArknightsBot.Vision.dll
    # Ta cần lùi ra thư mục gốc rồi vào bin
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Đường dẫn này đi từ src -> root -> bin
    dll_path = os.path.abspath(os.path.join(current_dir, "..", "..", "bin", "ArknightsBot.Vision.dll"))

    print(f"[PYTHON] Dang tim DLL tai: {dll_path}")

    if not os.path.exists(dll_path):
        print("[PYTHON] ERROR: Khong tim thay file DLL!")
        return

    try:
        # 2. Load DLL C++
        vision_lib = ctypes.CDLL(dll_path)
        
        # 3. Gọi hàm Sum từ C++
        a, b = 10, 50
        result = vision_lib.Sum(a, b)
        print(f"[PYTHON] Ket qua goi C++ Sum({a}, {b}) = {result}")

        # 4. Gọi hàm giả lập tìm ảnh
        vision_lib.FindImageMock.restype = ctypes.c_double # Khai báo kiểu trả về là số thực
        confidence = vision_lib.FindImageMock()
        print(f"[PYTHON] Do chinh xac nhan dien: {confidence}")

    except Exception as e:
        print(f"[PYTHON] EXCEPTION: {e}")

if __name__ == "__main__":
    main()