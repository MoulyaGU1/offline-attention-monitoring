import time
import threading
import pygetwindow as gw
import winsound
import tkinter as tk
import win32gui
import win32con
from ctypes import windll

# --- GLOBAL FLAGS (Keep these at the top) ---
FORCE_STOP = False
REMAINING_SECONDS = 0
IS_VISIBLE = False     
IS_BREACHED = False  

class FlowShield:
    def __init__(self):
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        
        # Windows Click-Through API
        hwnd = win32gui.GetParent(self.root.winfo_id())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

        self.trans_key = "#010101" 
        self.canvas = tk.Canvas(self.root, width=self.screen_w, height=self.screen_h, 
                               bg=self.trans_key, highlightthickness=0)
        self.canvas.pack()
        self.root.attributes("-transparentcolor", self.trans_key)

        # UI Elements
        self.green_border = self.canvas.create_rectangle(10, 10, self.screen_w-10, self.screen_h-10, outline="#00ff88", width=10, state='hidden')
        self.flicker_rect = self.canvas.create_rectangle(0, 50, self.screen_w, self.screen_h - 60, fill="#ff0055", state='hidden')
        
        # TIMER - Placed in the top right corner
        self.canvas_timer = self.canvas.create_text(self.screen_w - 50, 40, text="00:00", fill="#00ff88", font=("Consolas", 38, "bold"), anchor="ne")

        self.flicker_toggle = False
        self.update_ui_loop()

    def update_ui_loop(self):
        global REMAINING_SECONDS, IS_VISIBLE, FORCE_STOP, IS_BREACHED
        if IS_VISIBLE and not FORCE_STOP:
            self.root.attributes("-alpha", 1.0)
            self.root.lift()
            mins, secs = divmod(REMAINING_SECONDS, 60)
            self.canvas.itemconfig(self.canvas_timer, text=f"{mins:02d}:{secs:02d}")

            if IS_BREACHED:
                self.flicker_toggle = not self.flicker_toggle
                self.canvas.itemconfig(self.flicker_rect, state='normal' if self.flicker_toggle else 'hidden')
                self.canvas.itemconfig(self.green_border, state='hidden')
                self.canvas.itemconfig(self.canvas_timer, fill="#ff0055")
            else:
                self.canvas.itemconfig(self.flicker_rect, state='hidden')
                self.canvas.itemconfig(self.green_border, state='normal')
                self.canvas.itemconfig(self.canvas_timer, fill="#00ff88")
        else:
            self.root.attributes("-alpha", 0.0)
        self.root.after(150, self.update_ui_loop)

# --- HELPER FUNCTIONS (Must be outside the class) ---
def play_ambulance_siren():
    while IS_BREACHED and not FORCE_STOP:
        winsound.Beep(1200, 200)
        if not IS_BREACHED: break
        winsound.Beep(800, 200)

shield_app = None
def start_gui_thread():
    global shield_app
    shield_app = FlowShield()
    shield_app.root.mainloop()

threading.Thread(target=start_gui_thread, daemon=True).start()

# --- THE FUNCTION YOUR SERVER IS LOOKING FOR ---
def start_flow_lock(committed_apps, duration_mins):
    global REMAINING_SECONDS, IS_VISIBLE, IS_BREACHED, FORCE_STOP
    FORCE_STOP = False
    REMAINING_SECONDS = int(duration_mins) * 60
    target_list = [app.strip().lower() for app in committed_apps.split(',') if app.strip()]
    target_list.extend(["attention mapping", "127.0.0.1", "localhost", "python"])
    
    IS_VISIBLE = True
    is_currently_sirening = False

    while REMAINING_SECONDS > 0 and not FORCE_STOP:
        try:
            active_window = gw.getActiveWindow()
            title = active_window.title.lower() if (active_window and active_window.title) else "desktop"
            if not any(app in title for app in target_list):
                IS_BREACHED = True
                if not is_currently_sirening:
                    is_currently_sirening = True
                    threading.Thread(target=play_ambulance_siren, daemon=True).start()
            else:
                IS_BREACHED = False
                is_currently_sirening = False
            time.sleep(1)
            REMAINING_SECONDS -= 1
        except:
            time.sleep(1)
    IS_VISIBLE = False
    IS_BREACHED = False
# 1. Add this method inside your FlowShield class
def show_completion(self):
    """Triggers a high-visibility completion overlay."""
    def create_overlay():
        # Hide the flicker and border
        self.canvas.itemconfig(self.flicker_rect, state='hidden')
        self.canvas.itemconfig(self.green_border, state='hidden')
        
        # Create a semi-transparent dark overlay
        self.root.attributes("-alpha", 0.9)
        self.canvas.config(bg="#050505")
        self.root.attributes("-transparentcolor", "") # Show the background

        # Add "SESSION COMPLETED" Text in the center
        self.canvas.create_text(
            self.screen_w // 2, self.screen_h // 2 - 50,
            text="🎯 SESSION COMPLETED",
            fill="#00ff88",
            font=("Consolas", 48, "bold")
        )

        # Add a sub-text message
        self.canvas.create_text(
            self.screen_w // 2, self.screen_h // 2 + 30,
            text="Your focus session has been logged successfully.",
            fill="white",
            font=("Consolas", 18)
        )

        # Create a temporary button (using a canvas shape + text for click-through compatibility)
        # Note: Since the window is click-through, we'll auto-close after 5 seconds
        # or you can provide a keyboard shortcut instructions.
        self.root.after(5000, lambda: self.root.attributes("-alpha", 0.0))

    self.root.after(0, create_overlay)
# trackers/flow_lock.py


# ... other imports ...

    