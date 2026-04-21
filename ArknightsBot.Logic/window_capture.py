import win32gui
import win32ui
import win32con
import numpy as np
import cv2

class WindowCapture:
    def __init__(self, window_name=None):
        self.hwnd = None
        if window_name:
            def enum_cb(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if window_name.lower() in title.lower() or "mumu" in title.lower():
                        # Cửa sổ main của MuMu thường chứa MuMuPlayer hoặc MuMu Player
                        results.append(hwnd)

            hwnds = []
            win32gui.EnumWindows(enum_cb, hwnds)
            
            if hwnds:
                self.hwnd = hwnds[0]
            else:
                self.hwnd = win32gui.FindWindow(None, window_name)

            if not self.hwnd:
                raise Exception(f"Không tìm thấy cửa sổ: {window_name}")
            
            print(f">>> Đã bind vào cửa sổ: {win32gui.GetWindowText(self.hwnd)}")

    def screenshot(self):
        # Lấy kích thước vùng Client
        left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
        w = right - left
        h = bottom - top

        # Nếu bị thu nhỏ (minimized)
        if w <= 0 or h <= 0:
            return None

        # Tạo device context
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()

        # Tạo Bitmap
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)

        # Copy dữ liệu màn hình vào Bitmap
        old_bmp = cDC.SelectObject(dataBitMap)
        
        # Cách 1: Dùng PrintWindow (Hỗ trợ chụp ngầm, nhưng hay bị đen với giả lập)
        import ctypes
        result = ctypes.windll.user32.PrintWindow(self.hwnd, cDC.GetSafeHdc(), 3) 
        
        # Lấy byte ra kiểm tra xem có bị đen thui không
        bmpstr = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype='uint8')
        
        try:
            img.shape = (h, w, 4) # BGRA
        except ValueError:
            img = None

        # Kiểm tra xem ảnh có bị đen thui (toàn mã màu 0) do lỗi Hardware Acceleration không
        is_black_screen = False
        if img is not None:
            # Kiểm tra 3 kênh màu đầu tiên (BGR), bỏ qua kênh Alpha (A)
            # Nếu tất cả các điểm ảnh đều là 0 -> Ảnh đen thui
            if not np.any(img[..., :3]):
                is_black_screen = True
                
        # Nếu PrintWindow lỗi hoặc bị đen thui, chuyển sang Cách 2: Chụp xuyên thấu từ Desktop
        if result == 0 or is_black_screen or img is None:
            # Lấy toạ độ thực của Client Area trên màn hình Desktop
            point = win32gui.ClientToScreen(self.hwnd, (0, 0))
            screen_x, screen_y = point[0], point[1]
            
            desktop_hwnd = win32gui.GetDesktopWindow()
            desktop_dc = win32gui.GetWindowDC(desktop_hwnd)
            desktop_dc_obj = win32ui.CreateDCFromHandle(desktop_dc)
            
            # Chụp thực tế từ toạ độ màn hình (Bắt buộc giả lập phải đang hiển thị trên màn hình)
            cDC.BitBlt((0, 0), (w, h), desktop_dc_obj, (screen_x, screen_y), win32con.SRCCOPY)
            
            # Cập nhật lại ảnh
            bmpstr = dataBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            try:
                img.shape = (h, w, 4)
            except ValueError:
                img = None
                
            desktop_dc_obj.DeleteDC()
            win32gui.ReleaseDC(desktop_hwnd, desktop_dc)

        if img is not None:
            # Cắt bỏ kênh Alpha và chuyển về BGR
            img = img[..., :3]
            img = np.ascontiguousarray(img)

        # Giải phóng tài nguyên đúng cách để tránh tràn RAM
        cDC.SelectObject(old_bmp)
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        return img