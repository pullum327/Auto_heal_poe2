import tkinter as tk
from tkinter import ttk
import cv2
import pytesseract
import pyautogui
import threading
import time
import numpy as np
from pynput.keyboard import Controller
import sys
import io
import json
import os

CONFIG_FILE = "config.json"
pytesseract.pytesseract.tesseract_cmd = os.path.join(os.getcwd(), "Tesseract-OCR", "tesseract.exe")

keyboard = Controller()

# 預設的 MAX_HP, MAX_MP, LOW_HP_THRESHOLD, 和 LOW_MP_THRESHOLD
MAX_HP = 1000
MAX_MP = 6932
LOW_HP_THRESHOLD = 0.6
LOW_MP_THRESHOLD = 0.6

# 截屏區域 (默認值)
HP_REGION = (94, 811, 50, 30)
MP_REGION = (2358, 1090, 62, 21)

def save_config():
    """保存配置到文件"""
    config = {
        "HP_REGION": HP_REGION,
        "MP_REGION": MP_REGION,
        "MAX_HP": MAX_HP,
        "MAX_MP": MAX_MP
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)
    print("配置已保存")

def load_config():
    """從文件加載配置"""
    global HP_REGION, MP_REGION, MAX_HP, MAX_MP
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            HP_REGION = tuple(config["HP_REGION"])
            MP_REGION = tuple(config["MP_REGION"])
            MAX_HP = config["MAX_HP"]
            MAX_MP = config["MAX_MP"]
        print("配置已加載")
    else:
        print("未找到配置文件，使用默認值")
        
def get_value(region):
    """獲取螢幕指定區域的數值文字"""
    screenshot = pyautogui.screenshot(region=region)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
    _, frame = cv2.threshold(frame, 128, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(frame, config="--psm 7 -c tessedit_char_whitelist=0123456789/")
    return text.strip()

def select_region(region_name):
    """讓使用者通過 OpenCV 窗口框選區域，返回選中的區域座標"""
    global HP_REGION, MP_REGION,MAX_HP, MAX_MP
    start_point, end_point = None, None
    selecting = False

    def mouse_callback(event, x, y, flags, param):
        nonlocal start_point, end_point, selecting
        if event == cv2.EVENT_LBUTTONDOWN:
            selecting = True
            start_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and selecting:
            end_point = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            selecting = False
            end_point = (x, y)

    cv2.namedWindow("Select Region")
    cv2.setMouseCallback("Select Region", mouse_callback)

    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    while True:
        display_frame = frame.copy()
        if start_point and end_point:
            cv2.rectangle(display_frame, start_point, end_point, (0, 255, 0), 2)
        cv2.imshow("Select Region", display_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 13 and start_point and end_point:  # Enter 鍵確認選擇
            x1, y1 = start_point
            x2, y2 = end_point
            region = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            if region_name == "HP":
                HP_REGION = region
                print(f"選定 HP 區域: {HP_REGION}")
            elif region_name == "MP":
                MP_REGION = region
                print(f"選定 MP 區域: {MP_REGION}")
            save_config()
            break
        elif key == 27:  # Esc 鍵取消選擇
            print("取消選區")
            break

    cv2.destroyAllWindows()

def clean_value(text):
    """清理 OCR 偵測到的文字，僅保留數字"""
    return ''.join(filter(str.isdigit, text))


class HPMPMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("生命值與魔法值監控")
        self.root.geometry("400x600")
        self.root.config(bg="#f6e8dd")
        
        # 使用ttk樣式
        self.style = ttk.Style()
        self.style.configure("start.TButton", font=("Arial", 12), padding=6)

        # 創建標題標籤
        self.title_label = ttk.Label(self.root, text="Auto飲水", font=("Helvetica", 18, 'bold'), background="#f6e8dd")
        self.title_label.pack(pady=10)
        

        # 顯示生命值的標籤
        self.hp_label = ttk.Label(self.root, text="當前生命值: --", font=("Arial", 16), background="#f6e8dd")
        self.hp_label.pack(pady=10)

        # 選擇 HP 區域的按鈕
        self.select_hp_region_button = ttk.Button(self.root, text="選擇 HP 區域", command=lambda: self.select_region("HP"), style="start.TButton")
        self.select_hp_region_button.pack(pady=10)

        # 開始監控 HP 按鈕
        self.toggle_hp_button = ttk.Button(self.root, text="開啟 HP 監控", command=self.toggle_hp_monitoring, style="start.TButton")
        self.toggle_hp_button.pack(pady=10)

        # 顯示魔法值的標籤
        self.mp_label = ttk.Label(self.root, text="當前魔法值: --", font=("Arial", 16), background="#f6e8dd")
        self.mp_label.pack(pady=10)

        # 選擇 MP 區域的按鈕
        self.select_mp_region_button = ttk.Button(self.root, text="選擇 MP 區域", command=lambda: self.select_region("MP"), style="start.TButton")
        self.select_mp_region_button.pack(pady=10)

        # 開始監控 MP 按鈕
        self.toggle_mp_button = ttk.Button(self.root, text="開啟 MP 監控", command=self.toggle_mp_monitoring, style="start.TButton")
        self.toggle_mp_button.pack(pady=10)

        # 生命值和魔法值閾值調節
        self.threshold_frame = ttk.Frame(self.root)
        self.threshold_frame.pack(pady=20)

        ttk.Label(self.threshold_frame, text="HP 閾值: ", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.hp_threshold_var = tk.DoubleVar(value=LOW_HP_THRESHOLD)
        self.hp_threshold_slider = ttk.Scale(self.threshold_frame, from_=0.1, to=1.0, orient="horizontal", variable=self.hp_threshold_var, command=self.update_hp_label)
        self.hp_threshold_slider.grid(row=0, column=1, padx=5)

        self.hp_threshold_value_label = ttk.Label(self.threshold_frame, text=f"{LOW_HP_THRESHOLD:.1f}", font=("Arial", 12))
        self.hp_threshold_value_label.grid(row=0, column=2, padx=5)

        ttk.Label(self.threshold_frame, text="MP 閾值: ", font=("Arial", 12)).grid(row=1, column=0, padx=5)
        self.mp_threshold_var = tk.DoubleVar(value=LOW_MP_THRESHOLD)
        self.mp_threshold_slider = ttk.Scale(self.threshold_frame, from_=0.1, to=1.0, orient="horizontal", variable=self.mp_threshold_var, command=self.update_mp_label)
        self.mp_threshold_slider.grid(row=1, column=1, padx=5)

        self.mp_threshold_value_label = ttk.Label(self.threshold_frame, text=f"{LOW_MP_THRESHOLD:.1f}", font=("Arial", 12))
        self.mp_threshold_value_label.grid(row=1, column=2, padx=5)
        
        # MAX_HP 和 MAX_MP 設置
        self.max_values_frame = ttk.Frame(self.root)
        self.max_values_frame.pack(pady=20)

        ttk.Label(self.max_values_frame, text="MAX_HP: ", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.max_hp_var = tk.IntVar(value=MAX_HP)
        self.max_hp_entry = ttk.Entry(self.max_values_frame, textvariable=self.max_hp_var, width=10, font=("Arial", 12))
        self.max_hp_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.max_values_frame, text="MAX_MP: ", font=("Arial", 12)).grid(row=1, column=0, padx=5)
        self.max_mp_var = tk.IntVar(value=MAX_MP)
        self.max_mp_entry = ttk.Entry(self.max_values_frame, textvariable=self.max_mp_var, width=10, font=("Arial", 12))
        self.max_mp_entry.grid(row=1, column=1, padx=5)

        # 保存 MAX_HP 和 MAX_MP 的按鈕
        self.save_max_values_button = ttk.Button(self.root, text="保存 MAX_HP 和 MAX_MP", command=self.save_max_values, style="start.TButton")
        self.save_max_values_button.pack(pady=10)

        self.hp_monitoring = False
        self.mp_monitoring = False

    def update_hp_label(self, event=None):
        self.hp_threshold_value_label.config(text=f"{self.hp_threshold_var.get():.1f}")

    def update_mp_label(self, event=None):
        self.mp_threshold_value_label.config(text=f"{self.mp_threshold_var.get():.1f}")

    def select_region(self, region_name):
        """選擇區域並更新顯示"""
        select_region(region_name)
        if region_name == "HP":
            self.hp_label.config(text=f"HP 區域: {HP_REGION}")
        elif region_name == "MP":
            self.mp_label.config(text=f"MP 區域: {MP_REGION}")

    def monitor_hp(self):
        """後台線程，實時檢測生命值"""
        while self.hp_monitoring:
            try:
                hp_text = get_value(HP_REGION)
                hp_text = clean_value(hp_text)
                if hp_text:
                    current_hp = int(hp_text)
                    self.hp_label.config(text=f"當前生命值: {current_hp}")
                    if current_hp < MAX_HP * self.hp_threshold_var.get():
                        keyboard.press('1')
                        keyboard.release('1')
            except Exception as e:
                print(f"HP 監控出錯: {e}")
            time.sleep(0.7)

    def monitor_mp(self):
        """後台線程，實時檢測魔法值"""
        while self.mp_monitoring:
            try:

                mp_text = get_value(MP_REGION)
                mp_text = clean_value(mp_text)
                if mp_text:
                    current_mp = int(mp_text)
                    self.mp_label.config(text=f"當前魔法值: {current_mp}")
                    if current_mp < MAX_MP * self.mp_threshold_var.get():
                        keyboard.press('2')
                        time.sleep(0.1)
                        keyboard.release('2')
            except Exception as e:
                print(f"MP 監控出錯: {e}")
            time.sleep(0.08)

    def toggle_hp_monitoring(self):
        """切換 HP 監控"""
        if not self.hp_monitoring:
            self.hp_monitoring = True
            threading.Thread(target=self.monitor_hp, daemon=True).start()
            self.toggle_hp_button.config(text="停止 HP 監控")
        else:
            self.hp_monitoring = False
            self.toggle_hp_button.config(text="開啟 HP 監控")

    def toggle_mp_monitoring(self):
        """切換 MP 監控"""
        if not self.mp_monitoring:
            self.mp_monitoring = True
            threading.Thread(target=self.monitor_mp, daemon=True).start()
            self.toggle_mp_button.config(text="停止 MP 監控")
        else:
            self.mp_monitoring = False
            self.toggle_mp_button.config(text="開啟 MP 監控")
    def save_max_values(self):
            """保存 MAX_HP 和 MAX_MP"""
            global MAX_HP, MAX_MP
            MAX_HP = self.max_hp_var.get()
            MAX_MP = self.max_mp_var.get()
            save_config()

def main():
    load_config()
    
    root = tk.Tk()
    app = HPMPMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
