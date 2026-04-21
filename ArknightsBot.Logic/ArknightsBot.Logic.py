import sys
import os
import ctypes
import time
import glob
import json
import cv2
from adb_client import AdbClient
from window_capture import WindowCapture

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Đọc cấu hình
with open('settings.json', 'r') as f:
    config = json.load(f)

ADB_ADDRESS = config.get('adb_address', '127.0.0.1:7555')
ENHANCED_MODE = config.get('enhanced_mode', 0)
MUMU_PATH = config.get('mumu_path', '')

win_cap = None

# Nếu bật chế độ siêu tốc, khởi tạo Window Capture
if ENHANCED_MODE:
    print(">>> Đang bật chế độ Enhanced Mode (Chụp cửa sổ)...")
    try:
        # MuMu Player thường có tên cửa sổ là "MuMu Player" hoặc "MuMuPlayer-12.0"
        # Bạn có thể dùng tool 'Spy++' để xem chính xác tên cửa sổ
        win_cap = WindowCapture("MuMu Player") 
        print(">>> Đã kết nối với cửa sổ MuMu!")
    except Exception as e:
        print(f">>> LỖI: Không tìm thấy cửa sổ giả lập. Quay về dùng ADB. ({e})")
        ENHANCED_MODE = 0

def take_screenshot(adb):
    if ENHANCED_MODE and win_cap:
        # Cách 1: Chụp siêu tốc qua Window API (~15ms)
        img = win_cap.screenshot()
        if img is not None:
            # Encode thành mảng byte chuẩn PNG trên RAM
            _, buffer = cv2.imencode('.png', img)
            return buffer.tobytes()
        return None
    else:
        # Cách 2: Chụp truyền thống qua ADB (~500ms)
        return adb.capture_screen_to_memory()

# Giảm độ chính xác xuống một chút để dễ nhận diện hơn (0.85 thay vì 0.75)
THRESHOLD = 0.85 

SETTINGS = {
    "adb_address": "127.0.0.1:7555", # Mặc định là MuMu/LDPlayer
    "adb_path": "", # Để rỗng mặc định
    "region": "EN", # Mặc định là Global (EN)
    "delay_start": 2.0,
    "delay_squad": 5.0,
    "delay_settings": 0.5,
    "delay_retreat": 0.2,
    "delay_confirm": 0.2,
    "debug_mode": 0,
    "debug_delay": 1.0
}

def get_base_path():
    # Nếu đang chạy dạng file .exe (đã đóng gói)
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    
    # Nếu đang chạy code Python bình thường
    path = os.path.dirname(os.path.abspath(__file__))
    # Nếu đang ở trong thư mục ArknightsBot.Logic, nhảy ra thư mục gốc để tìm bin/templates
    if os.path.basename(path) == "ArknightsBot.Logic":
        return os.path.dirname(path)
    return path

def load_settings(current_dir):
    global SETTINGS
    json_path = os.path.join(current_dir, "settings.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                SETTINGS.update(data)
            print("[INIT] Settings loaded.")
        except: pass

adb_resolution = None
def get_adb_resolution(adb):
    global adb_resolution
    if adb_resolution: return adb_resolution
    try:
        output = adb.run_command("shell wm size")
        if output and "size:" in output:
            parts = output.strip().split(":")[-1].strip().split("x")
            adb_resolution = (int(parts[0]), int(parts[1]))
            return adb_resolution
    except:
        pass
    return None

def find_and_click(adb, vision_lib, current_dir, image_name, wait_after=1.0):
    try:
        region = SETTINGS.get("region", "EN")
        template_path = os.path.join(current_dir, "templates", region, image_name)
        if not os.path.exists(template_path): 
            print(f"[WARN] Thiếu ảnh mẫu: {template_path}")
            return False 

        # --- BƯỚC CẢI TIẾN: Lấy ảnh vào RAM (Hỗ trợ cả ADB và Window Capture) ---
        image_bytes = take_screenshot(adb)
        
        if image_bytes is None or len(image_bytes) == 0:
            print(f"[ERROR] ADB không trả về ảnh nào khi tìm '{image_name}' (Mất kết nối hoặc ADB lỗi)")
            sys.stdout.flush()
            return False

        # Lưu ảnh màn hình bot đang nhìn thấy ra file để debug NGAY LẬP TỨC
        debug_path = os.path.join(current_dir, "debug_screen.png")
        try:
            with open(debug_path, "wb") as f:
                f.write(image_bytes)
        except: pass

        # Chuyển đổi Bytes Python sang con trỏ C (C Array)
        ImageArrayType = ctypes.c_ubyte * len(image_bytes)
        c_image_data = ImageArrayType.from_buffer_copy(image_bytes)

        # Gọi hàm C++ mới
        x, y, sim = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_double(0.0)
        
        # Lưu ý: Hàm FindImageFromMemory nhận con trỏ byte và độ dài
        found = vision_lib.FindImageFromMemory(
            ctypes.cast(c_image_data, ctypes.POINTER(ctypes.c_ubyte)), 
            len(image_bytes),
            template_path.encode('utf-8'),
            ctypes.byref(x), ctypes.byref(y), ctypes.byref(sim)
        )

        if found:
            click_x, click_y = x.value, y.value

            # Xử lý lệch tọa độ: Window Size != ADB Size
            if ENHANCED_MODE and win_cap:
                adb_res = get_adb_resolution(adb)
                if adb_res:
                    import numpy as np
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    win_w = img.shape[1]
                    win_h = img.shape[0]
                    
                    adb_w, adb_h = adb_res
                    scale_x = adb_w / win_w
                    scale_y = adb_h / win_h
                    
                    click_x = int(click_x * scale_x)
                    click_y = int(click_y * scale_y)

            # Luôn in debug để người dùng dễ theo dõi nếu đang bật Debug Mode
            if SETTINGS.get("debug_mode", 0):
                print(f"[DEBUG] Search '{image_name}': Sim={sim.value:.4f} (Cần >= {THRESHOLD})")
                sys.stdout.flush()
                time.sleep(SETTINGS.get("debug_delay", 1.0))

            if sim.value >= THRESHOLD:
                print(f"[TURBO] Found '{image_name}' -> CLICK at ADB({click_x}, {click_y})!")
                sys.stdout.flush()
                adb.tap(click_x, click_y)
                
                # Logic sleep thông minh
                real_wait = max(wait_after, 0.1)
                if SETTINGS.get("debug_mode", 0):
                    print(f"[DEBUG] Sleep {real_wait}s after clicking {image_name}")
                    sys.stdout.flush()
                time.sleep(real_wait)
                return True
        else:
            if SETTINGS.get("debug_mode", 0):
                print(f"[DEBUG] Search '{image_name}': FAILED IN C++ DLL (Ảnh hỏng hoặc quá bé)")
                sys.stdout.flush()
            
        return False
    except Exception as e:
        # print(f"Error: {e}")
        return False

def main():
    print("--- ARKNIGHTS RAM-MODE FARM ---")
    sys.stdout.flush() 
    
    current_dir = get_base_path()
    load_settings(current_dir)

    bin_dir = os.path.join(current_dir, "bin") 
    vision_dll_path = os.path.join(bin_dir, "ArknightsBot.Vision.dll")

    if hasattr(os, 'add_dll_directory') and os.path.exists(bin_dir):
         os.add_dll_directory(bin_dir)

    # Load OpenCV dependencies
    opencv_files = glob.glob(os.path.join(bin_dir, "opencv_world*.dll"))
    if opencv_files:
        try: ctypes.CDLL(opencv_files[0]) 
        except: pass

    # Load Vision DLL
    try:
        vision_lib = ctypes.CDLL(vision_dll_path)
        vision_lib.FindImageFromMemory.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), 
            ctypes.c_int,                   
            ctypes.c_char_p,                
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_double)
        ]
        vision_lib.FindImageFromMemory.restype = ctypes.c_bool
    except:
        print("[CRITICAL] DLL ERROR - Check ArknightsBot.Vision.dll")
        return

    # --- SỬA LỖI Ở ĐÂY: DÙNG ADB CỦA MAA NẾU CÓ ---
    custom_adb_path = SETTINGS.get("adb_path", "")
    
    if custom_adb_path and os.path.exists(custom_adb_path):
        print(f"[INIT] Using Custom ADB from Settings: {custom_adb_path}")
        # Truyền đường dẫn ADB của MAA vào đây
        adb = AdbClient(adb_path=custom_adb_path) 
    else:
        print("[INIT] Using Internal ADB")
        adb = AdbClient() # Không có setting thì dùng mặc định
    # -----------------------------------------------

    # Kết nối tới địa chỉ (VD: 127.0.0.1:16384)
    target_address = SETTINGS.get("adb_address", "127.0.0.1:7555")
    print(f"[INIT] Connecting to ADB: {target_address}")

    if adb.connect(target_address):
        print(f"[SUCCESS] Connected to {target_address}")
    else:
        print(f"[WARN] Failed to connect to {target_address}. Trying default fallback...")
        if not adb.connect("127.0.0.1:5555"):
             print("[CRITICAL] Cannot connect to any Emulator!")

    print(">>> BOT READY (RAM MODE)...")
    sys.stdout.flush()

    while True:
        try:
            # Chỉ tập trung vào tìm nút Settings để thoát trận (Module Instant Win)
            # Vì người dùng sử dụng chung với MAA để vào trận.
            
            # 1. Settings 
            if find_and_click(adb, vision_lib, current_dir, "btn_settings.png", wait_after=SETTINGS["delay_settings"]):
                print("   -> Menu opened.")
                sys.stdout.flush()
                
                retreat_clicked = False
                for _ in range(5):
                    if find_and_click(adb, vision_lib, current_dir, "btn_retreat.png", wait_after=SETTINGS["delay_retreat"]):
                        retreat_clicked = True
                        break
                    time.sleep(0.1)

                if retreat_clicked:
                    for _ in range(5):
                        if find_and_click(adb, vision_lib, current_dir, "btn_confirm.png", wait_after=SETTINGS["delay_confirm"]):
                            break
                        time.sleep(0.1)
                        
                    print("   -> Skipping results...")
                    sys.stdout.flush()
                    # Chờ xíu để animation xong r bấm bừa ra ngoài (Ví dụ: tap ở tọa độ 50,50)
                    time.sleep(1)
                    adb.tap(50, 50)
                    
                    print("[STATS]: +1 Farmed")
                    print(">>> Done.")
                    sys.stdout.flush()
                    time.sleep(SETTINGS["delay_start"])
            sys.stdout.flush()

        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    main()
