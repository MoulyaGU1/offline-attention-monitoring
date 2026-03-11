import time
import threading
import pygetwindow as gw
from win10toast import ToastNotifier
import winsound
import tkinter as tk

# --- GLOBAL STATE & CONTROL FLAGS ---
toaster = ToastNotifier()
SHIELD_ENABLED = True
IS_PAUSED = False
FORCE_STOP = False
REMAINING_SECONDS = 0

class FlowShield:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.config(bg="black")
        
        # Hide the window immediately on startup
        self.root.attributes("-alpha", 0.0) 
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        
        try:
            from ctypes import windll
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            style = windll.user32.GetWindowLongW(hwnd, -20)
            windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20)
        except: pass

        self.border = tk.Frame(self.root, highlightthickness=10, highlightbackground="#00ff88", bg="black")
        self.border.pack(fill="both", expand=True)

        self.timer_label = tk.Label(
            self.border, text="00:00", fg="#00ff88", bg="black", 
            font=("Consolas", 24, "bold")
        )
        self.timer_label.place(x=self.screen_w - 200, y=50)

    def update_hud(self, seconds, color):
        mins, secs = divmod(seconds, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}", fg=color)
        self.border.config(highlightbackground=color)
        self.root.update()

    def trigger_glitch(self):
        def flash():
            for _ in range(3):
                self.border.config(highlightbackground="#ff0055")
                self.root.update()
                time.sleep(0.08)
                self.border.config(highlightbackground="black")
                self.root.update()
                time.sleep(0.04)
            self.border.config(highlightbackground="#ff0055")
        threading.Thread(target=flash, daemon=True).start()

    def show_completion_popup(self, app_name):
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        w, h = 400, 200
        x, y = (self.screen_w // 2) - (w // 2), (self.screen_h // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        popup.config(bg="#050505", highlightthickness=2, highlightbackground="#00ff88")

        tk.Label(popup, text="SESSION COMPLETED", fg="#00ff88", bg="#050505", font=("Consolas", 18, "bold")).pack(pady=20)
        tk.Label(popup, text=f"Focus preserved on: {app_name}", fg="white", bg="#050505", font=("Consolas", 10)).pack(pady=5)
        tk.Button(popup, text="[ DISMISS ]", bg="#00ff88", fg="#000", font=("Consolas", 10, "bold"), command=self.root.destroy).pack(pady=20)
        winsound.PlaySound("SystemExit", winsound.SND_ALIAS)

# --- GLOBAL SHIELD INSTANCE ---
shield = None

def run_shield_ui():
    global shield
    shield = FlowShield()
    shield.root.mainloop()

threading.Thread(target=run_shield_ui, daemon=True).start()

def start_flow_lock(committed_app, duration_mins):
    global REMAINING_SECONDS, IS_PAUSED, FORCE_STOP
    
    FORCE_STOP = False
    REMAINING_SECONDS = int(duration_mins) * 60
    target = committed_app.lower().strip()
    
    # ACTIVATE SHIELD VISIBILITY ONLY NOW
    if shield:
        shield.root.attributes("-alpha", 1.0)
    
    print(f"🔒 Flow Shield Engaged: {target}")

    while REMAINING_SECONDS > 0:
        if FORCE_STOP:
            if shield: shield.root.attributes("-alpha", 0.0)
            break

        if IS_PAUSED:
            if shield: shield.update_hud(REMAINING_SECONDS, "#ffcc00")
            time.sleep(1)
            continue

        try:
            active_window = gw.getActiveWindow()
            if not active_window or not active_window.title or target not in active_window.title.lower():
                if shield: 
                    shield.trigger_glitch()
                    shield.update_hud(REMAINING_SECONDS, "#ff0055")
                winsound.Beep(1000, 200)
            else:
                if shield: 
                    shield.root.attributes("-alpha", 1.0)
                    shield.update_hud(REMAINING_SECONDS, "#00ff88")

            time.sleep(1)
            REMAINING_SECONDS -= 1
        except:
            time.sleep(1)

    # --- SESSION END ---
    if not FORCE_STOP:
        if shield:
            shield.update_hud(0, "#00e5ff") 
            shield.show_completion_popup(committed_app)
    else:
        if shield: shield.root.attributes("-alpha", 0.0)