import sys
import os
import time
import threading
import ctypes
from ctypes import wintypes
import winsound
import tkinter as tk
from tkinter import ttk

user32 = ctypes.windll.user32
winmm = ctypes.windll.winmm
winmm.timeBeginPeriod(1)

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004
MOUSEEVENTF_MOVE     = 0x0001
VK_F6 = 0x75
VK_F8 = 0x77

class PrecisionClickEngine:
    def __init__(self):
        self.is_running = False
        self.clicks_per_second = 15
        self.hold_duration_ms = 35
        self.total_clicks = 0
        self.live_cps = 0
        self.lock = threading.Lock()
        self.worker_thread = None

    def execute_click(self):
        pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))

        user32.SetCursorPos(pt.x, pt.y)
        user32.mouse_event(MOUSEEVENTF_MOVE, 0, 0, 0, 0)
        time.sleep(0.002)

        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, pt.x, pt.y, 0, 0)
        time.sleep(self.hold_duration_ms / 1000.0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, pt.x, pt.y, 0, 0)

    def _worker_loop(self):
        while self.is_running:
            t0 = time.perf_counter()
            self.execute_click()

            with self.lock:
                self.total_clicks += 1
                self.live_cps += 1

            target_period = 1.0 / max(self.clicks_per_second, 1)
            elapsed = time.perf_counter() - t0
            remaining = target_period - elapsed
            if remaining > 0:
                time.sleep(remaining)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()

    def stop(self):
        self.is_running = False


class BongoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bongo Cat Steam AutoClicker")
        self.root.geometry("450x520")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.engine = PrecisionClickEngine()

        self.theme_bg = "#0d1117"
        self.theme_card = "#161b22"
        self.accent_pink = "#ff477e"
        self.accent_green = "#2ea043"
        self.accent_cyan = "#58a6ff"
        self.accent_yellow = "#f1e05a"
        self.text_primary = "#f0f6fc"
        self.text_secondary = "#8b949e"

        self.root.configure(bg=self.theme_bg)
        self._build_interface()
        self._init_global_hotkeys()

    def _build_interface(self):
        header_frame = tk.Frame(self.root, bg=self.theme_bg)
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(
            header_frame, 
            text="🐾 BONGO CAT STEAM CLICKER", 
            font=("Segoe UI Black", 16, "bold"), 
            fg=self.accent_pink, 
            bg=self.theme_bg
        ).pack(anchor="w")

        tk.Label(
            header_frame, 
            text="High-precision hardware mouse emulation for Steam games", 
            font=("Segoe UI", 8), 
            fg=self.text_secondary, 
            bg=self.theme_bg
        ).pack(anchor="w")

        status_card = tk.Frame(self.root, bg=self.theme_card, highlightthickness=1, highlightbackground="#30363d")
        status_card.pack(fill="x", padx=20, pady=10)

        self.label_status = tk.Label(
            status_card, 
            text="● STOPPED (PRESS F6)", 
            font=("Segoe UI", 11, "bold"), 
            fg="#f85149", 
            bg=self.theme_card
        )
        self.label_status.pack(pady=(12, 2))

        self.label_cps = tk.Label(
            status_card, 
            text="0 CLICKS/SEC", 
            font=("Segoe UI Black", 26, "bold"), 
            fg=self.accent_cyan, 
            bg=self.theme_card
        )
        self.label_cps.pack()

        self.label_total = tk.Label(
            status_card, 
            text="Total clicks: 0", 
            font=("Segoe UI", 9), 
            fg=self.text_secondary, 
            bg=self.theme_card
        )
        self.label_total.pack(pady=(2, 12))

        profile_container = tk.LabelFrame(
            self.root, 
            text=" Speed Profile ", 
            font=("Segoe UI", 9, "bold"), 
            fg=self.accent_yellow, 
            bg=self.theme_bg, 
            bd=1
        )
        profile_container.pack(fill="x", padx=20, pady=5)

        self.selected_profile = tk.StringVar(value="SAFE_FAST")

        speed_profiles = [
            ("⚡ 15 Clicks/sec (Steam Recommended - 100% Hit Rate)", "SAFE_FAST"),
            ("🚀 25 Clicks/sec (Turbo Fast)", "TURBO"),
            ("🔥 40 Clicks/sec (Max Frequency with Hold)", "INSANE"),
            ("🐾 8 Clicks/sec (Natural Safe Pace)", "NATURAL"),
        ]

        for title, identifier in speed_profiles:
            r = tk.Radiobutton(
                profile_container, 
                text=title, 
                value=identifier, 
                variable=self.selected_profile, 
                command=self._handle_profile_change,
                font=("Segoe UI", 9), 
                fg=self.text_primary, 
                bg=self.theme_bg,
                activebackground=self.theme_bg, 
                activeforeground=self.accent_yellow,
                selectcolor=self.theme_card,
                takefocus=False
            )
            r.pack(anchor="w", padx=10, pady=2)

        self.toggle_button = tk.Button(
            self.root, 
            text="▶ START CLICKS (F6)", 
            font=("Segoe UI", 12, "bold"), 
            fg="#ffffff", 
            bg=self.accent_green, 
            activebackground="#2c974b",
            activeforeground="#ffffff", 
            bd=0, 
            pady=12, 
            cursor="hand2", 
            takefocus=False,
            command=self.toggle_clicking
        )
        self.toggle_button.pack(fill="x", padx=20, pady=(15, 5))

        instructions_label = tk.Label(
            self.root, 
            text="💡 Instructions:\n1. Hover your cursor over Bongo Cat inside the Steam window.\n2. Press [F6] to toggle clicking on or off.", 
            font=("Segoe UI", 8), 
            justify="left",
            fg=self.text_secondary, 
            bg=self.theme_bg
        )
        instructions_label.pack(side="bottom", pady=10)

    def _handle_profile_change(self):
        mode = self.selected_profile.get()
        if mode == "SAFE_FAST":
            self.engine.clicks_per_second = 15
            self.engine.hold_duration_ms = 35
        elif mode == "TURBO":
            self.engine.clicks_per_second = 25
            self.engine.hold_duration_ms = 22
        elif mode == "INSANE":
            self.engine.clicks_per_second = 40
            self.engine.hold_duration_ms = 14
        elif mode == "NATURAL":
            self.engine.clicks_per_second = 8
            self.engine.hold_duration_ms = 50

    def toggle_clicking(self):
        if not self.engine.is_running:
            self.engine.start()
            self.label_status.config(text="● ACTIVE (CLICKING...)", fg=self.accent_green)
            self.toggle_button.config(text="⏹ STOP CLICKS (F6)", bg="#da3633", activebackground="#b62324")
            threading.Thread(target=lambda: winsound.Beep(1200, 80), daemon=True).start()
        else:
            self.engine.stop()
            self.label_status.config(text="● STOPPED", fg="#f85149")
            self.toggle_button.config(text="▶ START CLICKS (F6)", bg=self.accent_green, activebackground="#2c974b")
            threading.Thread(target=lambda: winsound.Beep(600, 80), daemon=True).start()

    def _init_global_hotkeys(self):
        def hotkey_listener():
            prev_f6_state = 0
            prev_f8_state = 0
            last_timestamp = time.perf_counter()

            while True:
                current_f6 = user32.GetAsyncKeyState(VK_F6) & 0x8000
                if current_f6 and not prev_f6_state:
                    self.root.after(0, self.toggle_clicking)
                prev_f6_state = current_f6

                current_f8 = user32.GetAsyncKeyState(VK_F8) & 0x8000
                if current_f8 and not prev_f8_state:
                    if self.engine.is_running:
                        self.root.after(0, self.toggle_clicking)
                prev_f8_state = current_f8

                now = time.perf_counter()
                elapsed = now - last_timestamp
                if elapsed >= 0.5:
                    with self.engine.lock:
                        rate = int(self.engine.live_cps / elapsed)
                        total = self.engine.total_clicks
                        self.engine.live_cps = 0
                    last_timestamp = now
                    try:
                        self.root.after(0, self._render_stats, rate, total)
                    except Exception:
                        break

                time.sleep(0.02)

        listener_thread = threading.Thread(target=hotkey_listener, daemon=True)
        listener_thread.start()

    def _render_stats(self, rate, total):
        self.label_cps.config(text=f"{rate} CLICKS/SEC")
        self.label_total.config(text=f"Total clicks: {total:,}")


def run_application():
    root = tk.Tk()
    app = BongoClickerApp(root)
    root.mainloop()
    winmm.timeEndPeriod(1)


if __name__ == "__main__":
    run_application()
