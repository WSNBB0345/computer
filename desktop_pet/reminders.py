"""Reminder scheduling utilities for the desktop pet."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List


@dataclass
class Reminder:
    """Reminder data parsed from configuration."""

    name: str
    interval_minutes: int
    message: str
    enabled: bool = True
    jitter: int = 5
    after_id: str | None = field(default=None, init=False)

    def interval_ms(self) -> int:
        base = max(self.interval_minutes, 1) * 60_000
        if self.jitter <= 0:
            return base
        delta = random.randint(-self.jitter, self.jitter) * 60_000
        return max(base + delta, 30_000)


class ReminderManager:
    """Schedules reminders using a Tk-like interface."""

    def __init__(
        self,
        tk_root: "tk.Misc",
        config: Iterable[Dict[str, object]],
        on_trigger: Callable[[Reminder], None],
    ) -> None:
        self._root = tk_root
        self._reminders: List[Reminder] = []
        for rem in config:
            data = dict(rem)
            data.setdefault("enabled", True)
            if "interval_minutes" in data:
                data["interval_minutes"] = int(data["interval_minutes"])
            if "jitter" in data:
                data["jitter"] = int(data["jitter"])
            self._reminders.append(Reminder(**data))
        self._on_trigger = on_trigger

    # Tkinter is only imported for type checking to avoid unnecessary dependency
    # at import time when running tests or building docs.
    try:  # pragma: no cover - optional import for typing
        import tkinter as tk  # type: ignore
    except Exception:  # pragma: no cover
        tk = None  # type: ignore

    def start(self) -> None:
        for reminder in self._reminders:
            self._schedule(reminder)

    def stop(self) -> None:
        for reminder in self._reminders:
            if reminder.after_id:
                self._root.after_cancel(reminder.after_id)
                reminder.after_id = None

    def _schedule(self, reminder: Reminder) -> None:
        if not reminder.enabled:
            return
        reminder.after_id = self._root.after(
            reminder.interval_ms(), lambda r=reminder: self._fire(r)
        )

    def _fire(self, reminder: Reminder) -> None:
        reminder.after_id = None
        self._on_trigger(reminder)
        self._schedule(reminder)
