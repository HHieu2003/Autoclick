"""
Module ghi lại tất cả hành động chuột và bàn phím
"""
import time
import json
from pynput import mouse, keyboard

class ActionRecorder:
    def __init__(self):
        self.actions = []
        self.is_recording = False
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        
    def start_recording(self):
        """Bắt đầu ghi hành động"""
        self.actions = []
        self.is_recording = True
        self.start_time = time.time()
        
        # Khởi tạo listeners
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move,
            on_scroll=self.on_scroll
        )
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        
        # Bắt đầu lắng nghe
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        print("🔴 Đang ghi... Nhấn F9 để dừng")
        
    def stop_recording(self):
        """Dừng ghi hành động"""
        self.is_recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
        print(f"⏹️ Đã ghi {len(self.actions)} hành động")
        return self.actions
    
    def get_relative_time(self):
        """Lấy thời gian tương đối từ lúc bắt đầu ghi"""
        return time.time() - self.start_time
    
    # === XỬ LÝ SỰ KIỆN CHUỘT ===
    
    def on_click(self, x, y, button, pressed):
        """Callback khi click chuột"""
        if not self.is_recording:
            return
            
        action = {
            'type': 'mouse_click',
            'x': x,
            'y': y,
            'button': str(button),
            'pressed': pressed,
            'time': self.get_relative_time()
        }
        self.actions.append(action)
        print(f"🖱️ Click {button} tại ({x}, {y})")
    
    def on_move(self, x, y):
        """Callback khi di chuyển chuột"""
        if not self.is_recording:
            return
        
        # Chỉ ghi khi có click hoặc khoảng cách thời gian đủ lớn
        if len(self.actions) > 0:
            last_action = self.actions[-1]
            # Ghi move nếu có click trước đó hoặc đã qua 0.05s
            if (last_action['type'] == 'mouse_click' and last_action['pressed']) or \
               (last_action['type'] == 'mouse_move' and 
                self.get_relative_time() - last_action['time'] > 0.05):
                
                action = {
                    'type': 'mouse_move',
                    'x': x,
                    'y': y,
                    'time': self.get_relative_time()
                }
                self.actions.append(action)
    
    def on_scroll(self, x, y, dx, dy):
        """Callback khi scroll chuột"""
        if not self.is_recording:
            return
            
        action = {
            'type': 'mouse_scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'time': self.get_relative_time()
        }
        self.actions.append(action)
        print(f"📜 Scroll tại ({x}, {y})")
    
    # === XỬ LÝ SỰ KIỆN BÀN PHÍM ===
    
    def on_key_press(self, key):
        """Callback khi nhấn phím"""
        if not self.is_recording:
            return
        
        # Dừng ghi khi nhấn F9
        try:
            if key == keyboard.Key.f9:
                return False  # Dừng listener
        except:
            pass
            
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key)
            
        action = {
            'type': 'key_press',
            'key': key_name,
            'time': self.get_relative_time()
        }
        self.actions.append(action)
        print(f"⌨️ Nhấn phím: {key_name}")
    
    def on_key_release(self, key):
        """Callback khi thả phím"""
        if not self.is_recording:
            return
            
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key)
            
        action = {
            'type': 'key_release',
            'key': key_name,
            'time': self.get_relative_time()
        }
        self.actions.append(action)
    
    def save_to_file(self, filename):
        """Lưu actions ra file JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.actions, f, indent=2, ensure_ascii=False)
        print(f"💾 Đã lưu vào {filename}")
    
    def load_from_file(self, filename):
        """Load actions từ file JSON"""
        with open(filename, 'r', encoding='utf-8') as f:
            self.actions = json.load(f)
        print(f"📂 Đã load {len(self.actions)} hành động từ {filename}")
        return self.actions
