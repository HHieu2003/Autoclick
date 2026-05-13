"""
Giao diện GUI cho ứng dụng Auto Clicker
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pynput import keyboard
from recorder import ActionRecorder
from player import ActionPlayer

class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Auto Clicker Pro")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        
        # Initialize modules
        self.recorder = ActionRecorder()
        self.player = ActionPlayer()
        self.current_file = None
        
        # Tạo thư mục macros nếu chưa có
        os.makedirs("macros", exist_ok=True)
        
        # Cấu hình phím tắt
        self.setup_emergency_stop()
        
        # Tạo giao diện
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo các widget cho GUI"""
        
        # === FRAME GHI HÀNH ĐỘNG ===
        record_frame = ttk.LabelFrame(self.root, text="📹 Ghi hành động", padding=10)
        record_frame.pack(fill="x", padx=10, pady=10)
        
        self.record_btn = tk.Button(
            record_frame, 
            text="🔴 Bắt đầu ghi (F9 để dừng)",
            command=self.start_recording,
            bg="#FF4444",
            fg="white",
            font=("Arial", 12, "bold"),
            height=2
        )
        self.record_btn.pack(fill="x", pady=5)
        
        self.status_label = tk.Label(
            record_frame,
            text="Trạng thái: Sẵn sàng",
            font=("Arial", 10)
        )
        self.status_label.pack()
        
        # === FRAME LƯU/LOAD ===
        file_frame = ttk.LabelFrame(self.root, text="💾 Quản lý Macro", padding=10)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(fill="x")
        
        tk.Button(
            btn_frame,
            text="💾 Lưu Macro",
            command=self.save_macro,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10)
        ).pack(side="left", expand=True, fill="x", padx=2)
        
        tk.Button(
            btn_frame,
            text="📂 Load Macro",
            command=self.load_macro,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10)
        ).pack(side="left", expand=True, fill="x", padx=2)
        
        self.file_label = tk.Label(
            file_frame,
            text="Chưa load macro nào",
            font=("Arial", 9),
            fg="gray"
        )
        self.file_label.pack(pady=5)
        
        # === FRAME CÀI ĐẶT PHÁT LẠI ===
        play_frame = ttk.LabelFrame(self.root, text="▶️ Cài đặt phát lại", padding=10)
        play_frame.pack(fill="x", padx=10, pady=10)
        
        # Số lần lặp
        repeat_frame = tk.Frame(play_frame)
        repeat_frame.pack(fill="x", pady=5)
        
        tk.Label(repeat_frame, text="Số lần lặp:", font=("Arial", 10)).pack(side="left")
        
        self.repeat_var = tk.IntVar(value=1)
        self.repeat_spinbox = tk.Spinbox(
            repeat_frame,
            from_=1,
            to=1000,
            textvariable=self.repeat_var,
            width=10,
            font=("Arial", 10)
        )
        self.repeat_spinbox.pack(side="left", padx=10)
        
        # Tốc độ phát
        speed_frame = tk.Frame(play_frame)
        speed_frame.pack(fill="x", pady=5)
        
        tk.Label(speed_frame, text="Tốc độ:", font=("Arial", 10)).pack(side="left")
        
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=0.1,
            to=5.0,
            resolution=0.1,
            orient="horizontal",
            variable=self.speed_var,
            length=300
        )
        self.speed_scale.pack(side="left", padx=10)
        
        self.speed_label = tk.Label(speed_frame, text="1.0x", font=("Arial", 10, "bold"))
        self.speed_label.pack(side="left")
        
        self.speed_var.trace('w', self.update_speed_label)
        
        # === FRAME ĐIỀU KHIỂN PHÁT ===
        control_frame = ttk.LabelFrame(self.root, text="🎮 Điều khiển", padding=10)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        btn_control = tk.Frame(control_frame)
        btn_control.pack(fill="x")
        
        self.play_btn = tk.Button(
            btn_control,
            text="▶️ PHÁT\n(F6)",
            command=self.start_playing,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 14, "bold"),
            height=2
        )
        self.play_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        self.stop_btn = tk.Button(
            btn_control,
            text="⏹️ DỪNG",
            command=self.stop_playing,
            bg="#FF9800",
            fg="white",
            font=("Arial", 14, "bold"),
            height=2,
            state="disabled"
        )
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # Nút dừng khẩn cấp
        self.emergency_stop_btn = tk.Button(
            btn_control,
            text="🛑 DỪNG KHẨN CẤP\n(F8)",
            command=self.emergency_stop,
            bg="#DC143C",
            fg="white",
            font=("Arial", 11, "bold"),
            height=2
        )
        self.emergency_stop_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # === INFO ===
        info_frame = tk.Frame(self.root)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            info_frame,
            text="💡 Mẹo: Di chuột vào góc trên-trái màn hình để dừng khẩn cấp",
            font=("Arial", 9),
            fg="blue"
        ).pack()
        
    def setup_emergency_stop(self):
        """Cấu hình phím tắt: F6 phát, F8 dừng khẩn cấp"""
        def on_key_press(key):
            try:
                if key == keyboard.Key.f6:
                    print("▶️ Phím F6 được nhấn!")
                    if not self.player.is_playing and not self.recorder.is_recording:
                        self.root.after(0, self.start_playing)
                elif key == keyboard.Key.f8:
                    print("🛑 Phím F8 được nhấn!")
                    self.root.after(0, self.emergency_stop)
            except:
                pass
        
        # Bắt đầu listener
        listener = keyboard.Listener(on_press=on_key_press)
        listener.daemon = True
        listener.start()
        
    def update_speed_label(self, *args):
        """Cập nhật label hiển thị tốc độ"""
        speed = self.speed_var.get()
        self.speed_label.config(text=f"{speed:.1f}x")
        
    def start_recording(self):
        """Bắt đầu ghi hành động"""
        self.record_btn.config(state="disabled")
        self.status_label.config(text="🔴 Đang ghi... Nhấn F9 để dừng", fg="red")
        
        def record_thread():
            self.recorder.start_recording()
            # Chờ đến khi user nhấn F9
            self.recorder.keyboard_listener.join()
            actions = self.recorder.stop_recording()
            
            # Cập nhật UI
            self.root.after(0, self.on_recording_stopped, len(actions))
        
        threading.Thread(target=record_thread, daemon=True).start()
        
    def on_recording_stopped(self, action_count):
        """Callback khi dừng ghi"""
        self.record_btn.config(state="normal")
        self.status_label.config(
            text=f"✅ Đã ghi {action_count} hành động",
            fg="green"
        )
        
        # Tự động hỏi lưu
        if action_count > 0:
            if messagebox.askyesno("Lưu macro", "Bạn có muốn lưu macro này không?"):
                self.save_macro()
        
    def save_macro(self):
        """Lưu macro ra file"""
        if not self.recorder.actions:
            messagebox.showwarning("Cảnh báo", "Chưa có hành động nào để lưu!")
            return
            
        filename = filedialog.asksaveasfilename(
            initialdir="macros",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            self.recorder.save_to_file(filename)
            self.current_file = filename
            self.file_label.config(text=f"📄 {os.path.basename(filename)}", fg="green")
            messagebox.showinfo("Thành công", "Đã lưu macro!")
            
    def load_macro(self):
        """Load macro từ file"""
        filename = filedialog.askopenfilename(
            initialdir="macros",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            actions = self.recorder.load_from_file(filename)
            self.player.load_actions(actions)
            self.current_file = filename
            self.file_label.config(
                text=f"📄 {os.path.basename(filename)} ({len(actions)} hành động)",
                fg="green"
            )
            messagebox.showinfo("Thành công", f"Đã load {len(actions)} hành động!")
            
    def start_playing(self):
        """Bắt đầu phát lại"""
        if not self.player.actions:
            messagebox.showwarning("Cảnh báo", "Chưa load macro nào!")
            return
            
        self.play_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="▶️ Đang phát...", fg="blue")
        
        repeat = self.repeat_var.get()
        speed = self.speed_var.get()
        
        def play_thread():
            try:
                self.player.play(repeat_times=repeat, speed=speed)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Có lỗi khi phát: {e}")
            finally:
                self.root.after(0, self.on_playing_stopped)
        
        threading.Thread(target=play_thread, daemon=True).start()
        
    def stop_playing(self):
        """Dừng phát"""
        self.player.stop()
        
    def emergency_stop(self):
        """Dừng khẩn cấp (dừng ghi hoặc phát)"""
        if self.is_recording:
            self.recorder.stop_recording()
            self.status_label.config(text="🛑 ĐÃ DỪNG KHẨN CẤP (Ghi)", fg="red")
        
        if self.player.is_playing:
            self.player.stop()
            self.status_label.config(text="🛑 ĐÃ DỪNG KHẨN CẤP (Phát)", fg="red")
        
        self.play_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.record_btn.config(state="normal")
        
        # Hiển thị thông báo
        messagebox.showwarning("Dừng khẩn cấp", "✋ Auto Click đã được dừng!")
    
    @property
    def is_recording(self):
        """Kiểm tra xem có đang ghi không"""
        return self.recorder.is_recording
        
    def on_playing_stopped(self):
        """Callback khi dừng phát"""
        self.play_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="✅ Đã hoàn thành", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerGUI(root)
    root.mainloop()
