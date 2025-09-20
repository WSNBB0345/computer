"""Main application for the desktop pet."""
from __future__ import annotations

import platform
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import tkinter as tk

from .config import CONFIG_FILE, ConfigManager, StateManager
from .pet import PetView
from .reminders import Reminder, ReminderManager


@dataclass
class PetState:
    """In-memory representation of the pet status."""

    mood: int
    affection: int
    last_interaction: float | None

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "PetState":
        return cls(
            mood=int(data.get("mood", 5)),
            affection=int(data.get("affection", 0)),
            last_interaction=float(data.get("last_interaction"))
            if data.get("last_interaction") is not None
            else None,
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "mood": self.mood,
            "affection": self.affection,
            "last_interaction": self.last_interaction,
        }


class DesktopPetApp:
    """Tkinter application orchestrating the pet behaviour."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        config_file = Path(config_path) if config_path else CONFIG_FILE
        self.config_manager = ConfigManager(path=config_file)
        self.state_manager = StateManager()
        self.config = self.config_manager.load()
        self.state = PetState.from_dict(self.state_manager.load())

        self.movement = self.config.get("movement", {})
        self.move_interval = int(self.movement.get("interval_ms", 80))
        self.move_step = int(self.movement.get("step", 5))
        self.bounds_margin = int(self.movement.get("bounds_margin", 50))

        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.bg_color = self.config.get("window", {}).get("background", "#000000")
        self._apply_transparency()

        width = int(self.config.get("window", {}).get("width", 220))
        height = int(self.config.get("window", {}).get("height", 220))
        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg=self.bg_color,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.pet = PetView(self.canvas)
        self.pet.update_mood(self.state.mood)
        self.pet.schedule_blink()

        self._drag_offset: Tuple[int, int] | None = None
        self._setup_bindings()
        self._create_menu()

        self.root.update_idletasks()
        self._position_window(width, height)
        self.root.deiconify()

        reminders_cfg = list(self.config.get("reminders", []))
        self.reminders = ReminderManager(self.root, reminders_cfg, self._on_reminder)
        self.reminders.start()

        self._tick()
        self._mood_decay_job = self.root.after(60_000, self._mood_decay)

    # ------------------------------------------------------------------
    def _apply_transparency(self) -> None:
        system = platform.system()
        self.root.config(bg=self.bg_color)
        if system == "Windows":
            try:
                self.root.wm_attributes("-transparentcolor", self.bg_color)
            except tk.TclError:
                pass
        elif system == "Darwin":
            try:
                self.root.attributes("-transparent", True)
            except tk.TclError:
                pass

    def _position_window(self, width: int, height: int) -> None:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - width - self.bounds_margin
        y = screen_height - height - self.bounds_margin
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self._window_pos = (x, y)

    def _setup_bindings(self) -> None:
        self.root.bind("<ButtonPress-1>", self._start_move)
        self.root.bind("<B1-Motion>", self._on_drag)
        self.root.bind("<ButtonRelease-1>", self._stop_move)
        self.root.bind("<Double-Button-1>", self._on_pet)
        self.root.bind("<Button-3>", self._show_menu)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _create_menu(self) -> None:
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="喂食", command=self.feed)
        self.menu.add_command(label="午休", command=self.take_nap)
        self.menu.add_separator()
        self.menu.add_command(label="重置心情", command=self.reset_mood)
        self.menu.add_command(label="退出", command=self.close)

    # Interaction handlers -------------------------------------------------
    def _start_move(self, event: tk.Event[tk.Misc]) -> None:  # type: ignore[type-var]
        self._drag_offset = (event.x, event.y)

    def _on_drag(self, event: tk.Event[tk.Misc]) -> None:  # type: ignore[type-var]
        if self._drag_offset is None:
            return
        dx = event.x_root - self._drag_offset[0]
        dy = event.y_root - self._drag_offset[1]
        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        self.root.geometry(f"{width}x{height}+{dx}+{dy}")
        self._window_pos = (dx, dy)

    def _stop_move(self, _event: tk.Event[tk.Misc]) -> None:  # type: ignore[type-var]
        self._drag_offset = None

    def _show_menu(self, event: tk.Event[tk.Misc]) -> None:  # type: ignore[type-var]
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _on_pet(self, _event: tk.Event[tk.Misc]) -> None:  # type: ignore[type-var]
        self.pet.bounce()
        self._change_mood(1)
        self.state.affection += 1
        self.state.last_interaction = time.time()
        self.pet.speak("谢谢你的摸摸~")
        self._persist_state()

    def feed(self) -> None:
        self.pet.bounce()
        self.pet.speak("好吃的! 精力满满~")
        self._change_mood(2)
        self.state.last_interaction = time.time()
        self._persist_state()

    def take_nap(self) -> None:
        self.pet.speak("呼……小睡一下。", duration=3000)
        self._change_mood(1)
        self.state.last_interaction = time.time()
        self._persist_state()

    def reset_mood(self) -> None:
        self.state.mood = 6
        self.pet.update_mood(self.state.mood)
        self.pet.speak("重新出发！")
        self._persist_state()

    def _on_reminder(self, reminder: Reminder) -> None:
        self.pet.speak(reminder.message)
        self.pet.bounce(intensity=6, cycles=3)

    # Movement and state updates ------------------------------------------
    def _tick(self) -> None:
        self._move_pet()
        self.root.after(self.move_interval, self._tick)

    def _move_pet(self) -> None:
        width = int(self.canvas["width"])
        height = int(self.canvas["height"])
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x, y = self._window_pos
        dx = random.randint(-self.move_step, self.move_step)
        dy = random.randint(-self.move_step, self.move_step)
        new_x = min(max(x + dx, self.bounds_margin), screen_width - width - self.bounds_margin)
        new_y = min(max(y + dy, self.bounds_margin), screen_height - height - self.bounds_margin)
        self.root.geometry(f"{width}x{height}+{new_x}+{new_y}")
        self._window_pos = (new_x, new_y)

    def _mood_decay(self) -> None:
        if self.state.last_interaction is None:
            elapsed = 3600
        else:
            elapsed = time.time() - self.state.last_interaction
        if elapsed > 1800 and self.state.mood > 1:
            self._change_mood(-1)
            self.pet.speak("好无聊…陪我玩嘛~", duration=5000)
            self.state.last_interaction = time.time()
            self._persist_state()
        self._mood_decay_job = self.root.after(120_000, self._mood_decay)

    def _change_mood(self, delta: int) -> None:
        self.state.mood = max(0, min(10, self.state.mood + delta))
        self.pet.update_mood(self.state.mood)

    def _persist_state(self) -> None:
        self.state_manager.save(self.state.to_dict())

    def close(self) -> None:
        self.reminders.stop()
        if hasattr(self, "_mood_decay_job"):
            self.root.after_cancel(self._mood_decay_job)
        self._persist_state()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
