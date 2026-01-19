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
        prefix = ""
        if self.device_serial:
            prefix = f"-s {self.device_serial} "

        full_cmd = f'"{self.adb_path}" {prefix}exec-out screencap -p'
        
        try:
            return subprocess.check_output(full_cmd, shell=True)
        except Exception:
            return None