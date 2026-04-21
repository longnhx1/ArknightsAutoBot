import os
import subprocess
import sys
import time

class AdbClient:
    def __init__(self, adb_path=None):
        self.device_serial = None
        
        # --- FIX LỖI TÌM ĐƯỜNG DẪN ADB ---
        if adb_path is None or adb_path == "":
            if getattr(sys, 'frozen', False):
                # Nếu đang chạy file .exe: Lấy đường dẫn của file .exe
                base_path = os.path.dirname(sys.executable)
            else:
                # Nếu chạy code thường: Lấy đường dẫn file code
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            # Trỏ đúng vào thư mục Release/adb/adb.exe
            self.adb_path = os.path.join(base_path, "adb", "adb.exe")
        else:
            self.adb_path = adb_path

    def run_command(self, cmd, use_serial=True):
        prefix = ""
        if use_serial and self.device_serial:
            prefix = f"-s {self.device_serial} "
            
        full_cmd = f'"{self.adb_path}" {prefix}{cmd}'
        
        try:
            # shell=True để tránh lỗi pop-up window
            result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8', errors='ignore').strip()
        except Exception:
            return None

    def connect(self, device_address):
        # Kiểm tra file adb.exe có tồn tại không
        if not os.path.exists(self.adb_path):
            print(f"[ERROR] ADB File not found at: {self.adb_path}")
            return False

        output = self.run_command(f"connect {device_address}", use_serial=False)
        if output and ("connected to" in output or "already connected" in output):
            self.device_serial = device_address
            return True
        return False

    def tap(self, x, y):
        self.run_command(f"shell input tap {x} {y}")

    def capture_screen_to_memory(self):
        # Thử lấy ảnh RAW siêu tốc trước (Bỏ cờ -p)
        cmd_raw = [self.adb_path]
        if self.device_serial:
            cmd_raw.extend(["-s", self.device_serial])
        cmd_raw.extend(["exec-out", "screencap"])
        
        try:
            import subprocess
            import struct
            import numpy as np
            import cv2
            
            raw_data = subprocess.check_output(cmd_raw, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Header ảnh RAW thường là 12 bytes (w, h, format)
            if len(raw_data) > 12:
                w, h, f = struct.unpack_from('<III', raw_data, 0)
                
                # Check offset based on data size (some devices use 16 bytes header)
                offset = 12
                if len(raw_data) - 16 == w * h * 4:
                    offset = 16
                
                if len(raw_data) - offset >= w * h * 4:
                    img_data = np.frombuffer(raw_data, dtype=np.uint8, count=w*h*4, offset=offset)
                    img = img_data.reshape((h, w, 4))
                    
                    # Convert RGBA to BGR
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                    
                    # Encode lại sang file byte PNG cho C++ DLL đọc trên RAM (cực nhanh)
                    success, buffer = cv2.imencode('.png', img)
                    if success:
                        return buffer.tobytes()
        except Exception:
            pass # Lỗi giải mã RAW hoặc thiếu thư viện, bỏ qua và dùng cách cũ

        # FALLBACK VỀ CÁCH CŨ (screencap -p) - Rất chậm nhưng chắc chắn chạy
        cmd_legacy = [self.adb_path]
        if self.device_serial:
            cmd_legacy.extend(["-s", self.device_serial])
        cmd_legacy.extend(["exec-out", "screencap", "-p"])
        
        try:
            import subprocess
            return subprocess.check_output(cmd_legacy, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            return None