import win32gui
import win32ui
import win32con
import numpy as np
import cv2

class WindowCapture:
    def __init__(self, window_name=None):
        self.hwnd = None
        if window_name:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception(f"Không tìm thấy cửa sổ: {window_name}")

    def screenshot(self):
        # Lấy kích thước vùng Client (vùng hiển thị game, bỏ qua thanh tiêu đề)
        left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
        w = right - left
        h = bottom - top

        # Tạo device context
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()

        # Tạo Bitmap
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)

        # Copy dữ liệu màn hình vào Bitmap
        cDC.SelectObject(dataBitMap)
        # Dùng PrintWindow để chụp (Nhanh hơn ADB rất nhiều)
        result = win32gui.PrintWindow(self.hwnd, cDC.GetHandleDC(), 2) 

        # Chuyển đổi sang dạng numpy array để OpenCV dùng được
        bmpinfo = dataBitMap.GetInfo()
        bmpstr = dataBitMap.GetBitmapBits(True)
        
        img = np.frombuffer(bmpstr, dtype='uint8')
        img.shape = (h, w, 4) # Ảnh Window thường có 4 kênh (BGRA)

        # Cắt bỏ kênh Alpha và chuyển về BGR
        img = img[..., :3]
        img = np.ascontiguousarray(img)

        # Giải phóng tài nguyên (Quan trọng để không bị tràn RAM)
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        return img