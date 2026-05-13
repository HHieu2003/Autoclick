"""
Module phát lại các hành động đã ghi
"""
import time
import pyautogui
from pynput.keyboard import Key, Controller as KeyboardController

class ActionPlayer:
    def __init__(self):
        self.actions = []
        self.is_playing = False
        self.keyboard = KeyboardController()
        self.speed_multiplier = 1.0  # Tốc độ phát lại (1.0 = bình thường)
        
        # Cấu hình pyautogui
        pyautogui.PAUSE = 0.001  # Giảm delay mặc định
        pyautogui.FAILSAFE = True  # Di chuột vào góc màn hình để dừng
        
    def load_actions(self, actions):
        """Load danh sách hành động"""
        self.actions = actions
        
    def play(self, repeat_times=1, speed=1.0):
        """
        Phát lại hành động
        
        Args:
            repeat_times: Số lần lặp lại
            speed: Tốc độ phát (1.0 = bình thường, 2.0 = nhanh gấp đôi)
        """
        self.is_playing = True
        self.speed_multiplier = speed
        
        print(f"▶️ Bắt đầu phát lại {repeat_times} lần với tốc độ {speed}x")
        
        for loop in range(repeat_times):
            if not self.is_playing:
                print("⏸️ Đã dừng phát")
                break
                
            print(f"\n🔄 Lần lặp {loop + 1}/{repeat_times}")
            self._play_once()
            
        self.is_playing = False
        print("✅ Hoàn thành!")
        
    def _play_once(self):
        """Phát lại một lần"""
        if not self.actions:
            print("⚠️ Không có hành động nào để phát")
            return
        
        for i, action in enumerate(self.actions):
            if not self.is_playing:
                break
            
            # Đợi theo thời gian đã ghi
            if i > 0:
                time_diff = action['time'] - self.actions[i-1]['time']
                adjusted_delay = time_diff / self.speed_multiplier
                time.sleep(max(0, adjusted_delay))
            
            # Thực hiện hành động
            self._execute_action(action)
    
    def _execute_action(self, action):
        """Thực thi một hành động cụ thể"""
        try:
            action_type = action['type']
            
            if action_type == 'mouse_click':
                self._execute_mouse_click(action)
                
            elif action_type == 'mouse_move':
                pyautogui.moveTo(action['x'], action['y'], duration=0)
                
            elif action_type == 'mouse_scroll':
                pyautogui.scroll(action['dy'], x=action['x'], y=action['y'])
                
            elif action_type == 'key_press':
                self._execute_key_press(action)
                
            elif action_type == 'key_release':
                self._execute_key_release(action)
                
        except Exception as e:
            print(f"❌ Lỗi khi thực thi {action_type}: {e}")
    
    def _execute_mouse_click(self, action):
        """Thực hiện click chuột"""
        button = 'left' if 'left' in action['button'].lower() else 'right'
        
        # Di chuyển đến vị trí
        pyautogui.moveTo(action['x'], action['y'], duration=0)
        
        # Click hoặc release
        if action['pressed']:
            pyautogui.mouseDown(button=button)
        else:
            pyautogui.mouseUp(button=button)
    
    def _execute_key_press(self, action):
        """Nhấn phím"""
        key = action['key']
        
        # Xử lý các phím đặc biệt
        key_mapping = {
            'Key.shift': 'shift',
            'Key.shift_r': 'shift',
            'Key.ctrl_l': 'ctrl',
            'Key.ctrl_r': 'ctrl',
            'Key.alt_l': 'alt',
            'Key.alt_r': 'alt',
            'Key.enter': 'enter',
            'Key.space': 'space',
            'Key.tab': 'tab',
            'Key.backspace': 'backspace',
            'Key.delete': 'delete',
            'Key.esc': 'esc',
        }
        
        key_to_press = key_mapping.get(key, key.replace('Key.', ''))
        pyautogui.keyDown(key_to_press)
    
    def _execute_key_release(self, action):
        """Thả phím"""
        key = action['key']
        key_mapping = {
            'Key.shift': 'shift',
            'Key.shift_r': 'shift',
            'Key.ctrl_l': 'ctrl',
            'Key.ctrl_r': 'ctrl',
            'Key.alt_l': 'alt',
            'Key.alt_r': 'alt',
            'Key.enter': 'enter',
            'Key.space': 'space',
            'Key.tab': 'tab',
        }
        
        key_to_release = key_mapping.get(key, key.replace('Key.', ''))
        pyautogui.keyUp(key_to_release)
    
    def stop(self):
        """Dừng phát"""
        self.is_playing = False

