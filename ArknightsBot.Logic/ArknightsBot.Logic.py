import sys
import os
import ctypes
import time
import glob
import json
from adb_client import AdbClient

# Giảm độ chính xác xuống một chút để nhận diện nhanh hơn
THRESHOLD = 0.75 

SETTINGS = {
    "adb_address": "127.0.0.1:7555", # Mặc định là MuMu/LDPlayer
    "adb_path": "", # Để rỗng mặc định
    "delay_start": 2.0,
    "delay_squad": 5.0,
    "delay_settings": 0.5,
    "delay_retreat": 0.2,
    "delay_confirm": 0.2
}

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

def find_and_click(adb, vision_lib, current_dir, image_name, wait_after=1.0):
    try:
        template_path = os.path.join(current_dir, "templates", image_name)
        if not os.path.exists(template_path): return False 

        # --- BƯỚC CẢI TIẾN: Lấy ảnh vào RAM (Không ghi file nữa) ---
        # Thời gian chụp: Giảm từ ~0.8s xuống ~0.3s
        image_bytes = adb.capture_screen_to_memory()
        
        if image_bytes is None or len(image_bytes) == 0:
            return False

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

        if found and sim.value >= THRESHOLD:
            print(f"[TURBO] Found '{image_name}' ({sim.value:.2f}) -> CLICK!")
            adb.tap(x.value, y.value)
            
            # Logic sleep thông minh
            real_wait = max(wait_after, 0.1)
            time.sleep(real_wait)
            return True
        
        return False
    except Exception as e:
        # print(f"Error: {e}")
        return False

def main():
    print("--- ARKNIGHTS RAM-MODE FARM ---")
    sys.stdout.flush() 
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    load_settings(current_dir)

    bin_dir = os.path.abspath(os.path.join(current_dir, "..", "bin"))
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
            # 1. Start 
            if find_and_click(adb, vision_lib, current_dir, "btn_start.png", wait_after=SETTINGS["delay_start"]):
                continue 

            # 2. Squad
            if find_and_click(adb, vision_lib, current_dir, "btn_squad.png", wait_after=SETTINGS["delay_squad"]):
                continue

            # 3. Settings 
            if find_and_click(adb, vision_lib, current_dir, "btn_settings.png", wait_after=SETTINGS["delay_settings"]):
                print("   -> Menu opened.")
                
                retreat_clicked = False
                for _ in range(5):
                    if find_and_click(adb, vision_lib, current_dir, "btn_retreat.png", wait_after=SETTINGS["delay_retreat"]):
                        retreat_clicked = True
                        break
                    time.sleep(0.3)
                
                if retreat_clicked:
                    time.sleep(0.5)
                    if find_and_click(adb, vision_lib, current_dir, "btn_confirm.png", wait_after=0.2):
                        print("   -> Skipping results...")
                        for _ in range(3):
                            adb.tap(500, 500)
                            time.sleep(0.2)
                        
                        print("[STATS]: +1 Farmed") 
                        print(">>> Done.")

            time.sleep(0.2)
            sys.stdout.flush()

        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    main()
