# File: D:\Auto\Arknights\Project\ArknightsAutoBot\ArknightsBot.Logic\adb_client.py
import os
import subprocess
import time

class AdbClient:
    def __init__(self, adb_path=None):
        # Tự động tìm adb.exe trong thư mục 'adb' nằm cùng chỗ với file code này
        if adb_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.adb_path = os.path.join(current_dir, "adb", "adb.exe")
        else:
            self.adb_path = adb_path

    def run_command(self, cmd):
        """Chạy lệnh ADB ngầm"""
        if not os.path.exists(self.adb_path):
            print(f"[ADB ERROR] Khong tim thay ADB tai: {self.adb_path}")
            return None

        full_cmd = f'"{self.adb_path}" {cmd}'
        try:
            # shell=True để chạy lệnh hệ thống mượt hơn trên Windows
            result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8', errors='ignore').strip()
        except subprocess.CalledProcessError as e:
            return None

    def connect(self, device_address="127.0.0.1:7555"):
        """Kết nối MuMu Player (Port mặc định 7555)"""
        print(f"[ADB] Dang ket noi toi {device_address}...")
        self.run_command("disconnect") # Ngắt kết nối cũ cho sạch
        result = self.run_command(f"connect {device_address}")
        
        # Kiểm tra danh sách thiết bị
        devices = self.run_command("devices")
        if devices and device_address in devices and "offline" not in devices:
            print(f"[ADB] Ket noi THANH CONG.")
            return True
        else:
            print(f"[ADB] Ket noi THAT BAI. Hay bat MuMu Player len.")
            return False

    def capture_screen(self, save_path):
        """Chụp màn hình -> Lưu vào máy tính"""
        # 1. Chụp lưu vào bộ nhớ giả lập
        self.run_command(f"shell screencap -p /sdcard/screen.png")
        # 2. Kéo từ giả lập về máy tính
        self.run_command(f"pull /sdcard/screen.png \"{save_path}\"")
        
        return os.path.exists(save_path)

    def tap(self, x, y):
        """Click vào tọa độ (x, y)"""
        self.run_command(f"shell input tap {x} {y}")
        print(f"[ADB] Clicked ({x}, {y})")