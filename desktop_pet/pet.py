"""Visual representation and simple animations for the desktop pet."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

import tkinter as tk


@dataclass
class MoodPalette:
    """Simple helper to convert mood value to colors."""

    happy: str = "#FFE066"
    neutral: str = "#FFD6A5"
    sad: str = "#B7B7A4"

    def color_for(self, mood: int) -> str:
        clamped = max(0, min(10, mood))
        if clamped >= 7:
            return self.happy
        if clamped <= 3:
            return self.sad
        return self.neutral


class PetView:
    """Tkinter based rendering helper."""

    def __init__(self, canvas: tk.Canvas, palette: Optional[MoodPalette] = None) -> None:
        self.canvas = canvas
        self.palette = palette or MoodPalette()
        self.bubble_id: Optional[int] = None
        self._bubble_after: Optional[str] = None
        self._blink_after: Optional[str] = None
        self._drawing_ids = self._create_pet()

    def _create_pet(self) -> dict[str, int]:
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])
        center_x = w // 2
        center_y = h // 2 + 10

        body = self.canvas.create_oval(
            center_x - 55,
            center_y - 55,
            center_x + 55,
            center_y + 55,
            fill=self.palette.happy,
            outline="",
        )
        belly = self.canvas.create_oval(
            center_x - 35,
            center_y - 20,
            center_x + 35,
            center_y + 45,
            fill="#FFF3B0",
            outline="",
        )
        left_eye = self.canvas.create_oval(
            center_x - 25,
            center_y - 15,
            center_x - 5,
            center_y + 10,
            fill="#1C1C1C",
            outline="",
        )
        right_eye = self.canvas.create_oval(
            center_x + 5,
            center_y - 15,
            center_x + 25,
            center_y + 10,
            fill="#1C1C1C",
            outline="",
        )
        blush_left = self.canvas.create_oval(
            center_x - 45,
            center_y + 10,
            center_x - 15,
            center_y + 30,
            fill="#FFA8A8",
            outline="",
        )
        blush_right = self.canvas.create_oval(
            center_x + 15,
            center_y + 10,
            center_x + 45,
            center_y + 30,
            fill="#FFA8A8",
            outline="",
        )
        mouth = self.canvas.create_line(
            center_x - 25,
            center_y + 30,
            center_x,
            center_y + 40,
            center_x + 25,
            center_y + 30,
            smooth=True,
            width=4,
            fill="#6B705C",
        )
        tail = self.canvas.create_arc(
            center_x + 40,
            center_y - 10,
            center_x + 120,
            center_y + 40,
            start=200,
            extent=140,
            style=tk.ARC,
            outline="#FFE066",
            width=16,
        )
        return {
            "body": body,
            "belly": belly,
            "left_eye": left_eye,
            "right_eye": right_eye,
            "blush_left": blush_left,
            "blush_right": blush_right,
            "mouth": mouth,
            "tail": tail,
        }

    def update_mood(self, mood: int) -> None:
        """Adjust colors and expressions to match mood."""

        color = self.palette.color_for(mood)
        self.canvas.itemconfigure(self._drawing_ids["body"], fill=color)
        self.canvas.itemconfigure(self._drawing_ids["tail"], outline=color)

        center_x = self._center_x
        center_y = self._center_y
        if mood >= 7:
            points = [center_x - 25, center_y + 32, center_x, center_y + 45, center_x + 25, center_y + 32]
        elif mood <= 3:
            points = [center_x - 25, center_y + 38, center_x, center_y + 30, center_x + 25, center_y + 38]
        else:
            points = [center_x - 25, center_y + 35, center_x, center_y + 40, center_x + 25, center_y + 35]
        self.canvas.coords(self._drawing_ids["mouth"], *points)

        if mood <= 3:
            self.canvas.itemconfigure(self._drawing_ids["blush_left"], state=tk.HIDDEN)
            self.canvas.itemconfigure(self._drawing_ids["blush_right"], state=tk.HIDDEN)
        else:
            self.canvas.itemconfigure(self._drawing_ids["blush_left"], state=tk.NORMAL)
            self.canvas.itemconfigure(self._drawing_ids["blush_right"], state=tk.NORMAL)

    @property
    def _center_x(self) -> int:
        return int(self.canvas["width"]) // 2

    @property
    def _center_y(self) -> int:
        return int(self.canvas["height"]) // 2 + 10

    def speak(self, message: str, duration: int = 4000) -> None:
        """Display a speech bubble for a limited duration."""

        if self.bubble_id is not None:
            self.canvas.delete(self.bubble_id)
            self.bubble_id = None
        if self._bubble_after is not None:
            self.canvas.after_cancel(self._bubble_after)
            self._bubble_after = None

        self.bubble_id = self.canvas.create_text(
            self._center_x,
            35,
            text=message,
            font=("Microsoft YaHei", 12, "bold"),
            fill="#FFFFFF",
            width=int(self.canvas["width"]) - 40,
        )
        bubble_rect = self.canvas.bbox(self.bubble_id)
        if bubble_rect:
            pad = 10
            rect_id = self.canvas.create_rectangle(
                bubble_rect[0] - pad,
                bubble_rect[1] - pad,
                bubble_rect[2] + pad,
                bubble_rect[3] + pad,
                fill="#495057",
                outline="",
            )
            self.canvas.tag_lower(rect_id, self.bubble_id)
        self._bubble_after = self.canvas.after(duration, self.clear_speech)

    def clear_speech(self) -> None:
        if self.bubble_id is not None:
            self.canvas.delete(self.bubble_id)
            self.bubble_id = None
        if self._bubble_after is not None:
            self.canvas.after_cancel(self._bubble_after)
            self._bubble_after = None

    def bounce(self, intensity: int = 8, cycles: int = 2) -> None:
        """Play a small bounce animation."""

        def _step(count: int, direction: int) -> None:
            if count <= 0:
                return
            self.canvas.move(tk.ALL, 0, -direction * intensity)
            self.canvas.after(80, lambda: _step(count - 1, -direction))

        _step(cycles * 2, 1)

    def schedule_blink(self) -> None:
        if self._blink_after is not None:
            self.canvas.after_cancel(self._blink_after)
        delay = random.randint(4_000, 9_000)
        self._blink_after = self.canvas.after(delay, self._blink)

    def _blink(self) -> None:
        left_eye = self._drawing_ids["left_eye"]
        right_eye = self._drawing_ids["right_eye"]
        left_coords = self.canvas.coords(left_eye)
        right_coords = self.canvas.coords(right_eye)

        def close_eyes() -> None:
            self.canvas.coords(
                left_eye,
                left_coords[0],
                (left_coords[1] + left_coords[3]) / 2 - 1,
                left_coords[2],
                (left_coords[1] + left_coords[3]) / 2 + 1,
            )
            self.canvas.coords(
                right_eye,
                right_coords[0],
                (right_coords[1] + right_coords[3]) / 2 - 1,
                right_coords[2],
                (right_coords[1] + right_coords[3]) / 2 + 1,
            )
            self.canvas.after(120, open_eyes)

        def open_eyes() -> None:
            self.canvas.coords(left_eye, *left_coords)
            self.canvas.coords(right_eye, *right_coords)
            self.schedule_blink()

        close_eyes()
