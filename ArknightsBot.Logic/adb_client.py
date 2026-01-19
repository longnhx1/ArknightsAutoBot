import os
import subprocess
import time

class AdbClient:
    def __init__(self, adb_path=None):
        # LOGIC 1: Xử lý đường dẫn ADB (Custom hoặc Mặc định)
        if adb_path is None or adb_path == "":
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.adb_path = os.path.join(current_dir, "adb", "adb.exe")
        else:
            self.adb_path = adb_path
        
        # LOGIC 2: Biến lưu địa chỉ để tránh lỗi "More than one device"
        self.device_serial = None

    def run_command(self, cmd, use_serial=True):
        """
        Chạy lệnh ADB.
        use_serial=True: Tự động thêm -s <ip:port> để chỉ định thiết bị.
        """
        # Tự động thêm cờ -s nếu đã kết nối
        prefix = ""
        if use_serial and self.device_serial:
            prefix = f"-s {self.device_serial} "
            
        full_cmd = f'"{self.adb_path}" {prefix}{cmd}'
        
        try:
            # shell=True để chạy lệnh trên Windows console
            result = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            return None

    def connect(self, device_address):
        # Khi connect thì không cần -s (use_serial=False)
        output = self.run_command(f"connect {device_address}", use_serial=False)
        
        # Kiểm tra kết nối thành công
        if output and ("connected to" in output or "already connected" in output):
            self.device_serial = device_address # LƯU LẠI ĐỊA CHỈ (QUAN TRỌNG)
            return True
        return False

    def tap(self, x, y):
        # Hàm này gọi run_command -> Tự động có -s -> Không bị lỗi nhầm thiết bị
        self.run_command(f"shell input tap {x} {y}")

    # --- HÀM MỚI: LẤY ẢNH TRỰC TIẾP VÀO RAM ---
    def capture_screen_to_memory(self):
        """
        Dùng lệnh 'exec-out' để lấy luồng dữ liệu nhị phân (binary).
        Đã thêm logic chọn đúng thiết bị (-s).
        """
        # Xây dựng lệnh thủ công vì hàm này trả về bytes, không dùng run_command
        prefix = ""
        if self.device_serial:
            prefix = f"-s {self.device_serial} "

        full_cmd = f'"{self.adb_path}" {prefix}exec-out screencap -p'
        
        try:
            return subprocess.check_output(full_cmd, shell=True)
        except Exception as e:
            print(f"[ADB ERROR] Capture failed: {e}")
            return None