import tkinter as tk
from threading import Thread
import time

class FlowShield:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True) # Remove title bar
        self.root.attributes("-topmost", True) # Stay on top
        self.root.attributes("-transparentcolor", "black") # Make black pixels transparent
        self.root.config(bg="black")
        
        # Set to full screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        
        # Allow clicks to pass through (Windows only)
        try:
            from ctypes import windll
            gwl_exstyle = -20
            ws_ex_layered = 0x80000
            ws_ex_transparent = 0x20
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            style = windll.user32.GetWindowLongW(hwnd, gwl_exstyle)
            windll.user32.SetWindowLongW(hwnd, gwl_exstyle, style | ws_ex_layered | ws_ex_transparent)
        except:
            pass

        # Create the border frame
        self.border = tk.Frame(self.root, highlightthickness=4, highlightbackground="#00ff88", bg="black")
        self.border.pack(fill="both", expand=True)
        
        self.active_color = "#00ff88" # Neon Green

    def update_status(self, is_distracted):
        if is_distracted:
            self.trigger_glitch()
        else:
            self.border.config(highlightbackground="#00ff88")

    def trigger_glitch(self):
        """Creates a red flickering effect to signal a distraction."""
        def flash():
            for _ in range(5):
                self.border.config(highlightbackground="#ff0055") # Neon Red
                self.root.update()
                time.sleep(0.1)
                self.border.config(highlightbackground="black")
                self.root.update()
                time.sleep(0.05)
            self.border.config(highlightbackground="#ff0055")
        
        Thread(target=flash).start()

    def run(self):
        self.root.mainloop()

# Global instance for the tracker to use
shield = None

def start_shield_thread():
    global shield
    shield = FlowShield()
    shield.run()