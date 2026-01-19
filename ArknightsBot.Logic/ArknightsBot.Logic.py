import sys
import os
import ctypes
import time
import glob # Library to find files with patterns like *.dll
from adb_client import AdbClient

# Config match threshold
THRESHOLD = 0.8

def find_and_click(adb, vision_lib, current_dir, image_name, wait_after=1.0):
    try:
        screen_path = os.path.join(current_dir, "screen_temp.png")
        template_path = os.path.join(current_dir, "templates", image_name)
        
        # Check if template exists
        if not os.path.exists(template_path):
            return False 

        # Capture screen
        adb.capture_screen(screen_path)
        
        # Call C++ Vision
        x, y, sim = ctypes.c_int(0), ctypes.c_int(0), ctypes.c_double(0.0)
        found = vision_lib.FindImage(
            screen_path.encode('utf-8'), 
            template_path.encode('utf-8'),
            ctypes.byref(x), ctypes.byref(y), ctypes.byref(sim)
        )

        # Check result
        if found and sim.value >= THRESHOLD:
            print(f"[ACTION] Found '{image_name}' (Sim: {sim.value:.2f}) -> Click at ({x.value}, {y.value})")
            adb.tap(x.value, y.value)
            time.sleep(wait_after)
            return True
        
        return False
    except Exception as e:
        print(f"[ERROR] Scan failed: {e}")
        return False

def main():
    print("--- ARKNIGHTS AUTO FARM & SURRENDER ---")
    sys.stdout.flush() 
    
    # 1. SETUP PATHS
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to Project folder, then into bin
    bin_dir = os.path.abspath(os.path.join(current_dir, "..", "bin"))
    vision_dll_path = os.path.join(bin_dir, "ArknightsBot.Vision.dll")

    print(f"[INFO] Bin Directory: {bin_dir}")

    # Fix for Python 3.8+ (Secure DLL loading)
    if hasattr(os, 'add_dll_directory'):
        if os.path.exists(bin_dir):
            os.add_dll_directory(bin_dir)
        else:
            print(f"[CRITICAL] Bin directory not found at: {bin_dir}")
            return

    # 2. PRE-LOAD OPENCV (CRITICAL FIX)
    # This ensures dependencies are loaded before loading the Vision DLL
    opencv_files = glob.glob(os.path.join(bin_dir, "opencv_world*.dll"))
    if opencv_files:
        try:
            print(f"[INIT] Pre-loading OpenCV: {os.path.basename(opencv_files[0])}")
            ctypes.CDLL(opencv_files[0]) 
        except Exception as e:
            print(f"[WARN] Failed to pre-load OpenCV: {e}")
    else:
        print(f"[WARN] No 'opencv_world*.dll' found in bin folder! Vision might fail.")

    # 3. LOAD VISION DLL
    try:
        vision_lib = ctypes.CDLL(vision_dll_path)
        # Define C++ function signature
        vision_lib.FindImage.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p, 
            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), 
            ctypes.POINTER(ctypes.c_double)
        ]
        vision_lib.FindImage.restype = ctypes.c_bool
        print("[INIT] Vision Engine Loaded Successfully.")
    except Exception as e:
        print(f"[CRITICAL] FAILED TO LOAD VISION DLL: {e}")
        print("Check if 'opencv_worldXXX.dll' is in the bin folder.")
        return

    # 4. CONNECT ADB
    adb = AdbClient()
    # Try MuMu port first, then BlueStacks/LD
    if not adb.connect("127.0.0.1:7555"):
        adb.connect("127.0.0.1:5555")

    print(">>> BOT STARTED. WAITING FOR IMAGES...")
    sys.stdout.flush()

    # 5. MAIN LOOP
    while True:
        try:
            # --- STATE 1: MISSION START (Blue Button) ---
            if find_and_click(adb, vision_lib, current_dir, "btn_start.png", wait_after=2.0):
                print("   -> Mission Start clicked. Waiting for Squad selection...")
                continue 

            # --- STATE 2: SQUAD CONFIRM (Red/Blue Button) ---
            if find_and_click(adb, vision_lib, current_dir, "btn_squad.png", wait_after=5.0):
                print("   -> Squad Confirmed! Entering battle...")
                continue

            # --- STATE 3: IN BATTLE (Settings Gear Icon) ---
            if find_and_click(adb, vision_lib, current_dir, "btn_settings.png", wait_after=2.0):
                print("   -> In-battle detected. Initiating surrender...")
                
                # Try to click Retreat
                retreat_clicked = False
                for _ in range(5):
                    if find_and_click(adb, vision_lib, current_dir, "btn_retreat.png", wait_after=1.5):
                        retreat_clicked = True
                        break
                    time.sleep(1)
                
                # Confirm Retreat
                if retreat_clicked:
                    time.sleep(1)
                    if find_and_click(adb, vision_lib, current_dir, "btn_confirm.png", wait_after=4.0):
                        # Spam click center to skip results
                        adb.tap(500, 500)
                        time.sleep(1)
                        adb.tap(500, 500)
                        
                        # Signal C# to count
                        print("[STATS]: +1 Farmed") 
                        print(">>> Battle finished. Looking for new battle...")

            time.sleep(1.5)
            sys.stdout.flush()

        except KeyboardInterrupt:
            print("Bot stopped by user.")
            break
        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()