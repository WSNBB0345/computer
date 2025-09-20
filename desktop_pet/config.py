"""Configuration and persistent state helpers for the desktop pet."""
from __future__ import annotations

import json
import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

APP_DIR = Path.home() / ".desktop_pet"
CONFIG_FILE = APP_DIR / "config.json"
STATE_FILE = APP_DIR / "state.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "pet_name": "Mochi",
    "window": {"width": 220, "height": 220, "background": "#000000"},
    "movement": {
        "step": 5,
        "interval_ms": 70,
        "bounds_margin": 50,
    },
    "reminders": [
        {
            "name": "stretch",
            "interval_minutes": 60,
            "message": "起来活动一下，放松身体~",
            "enabled": True,
        },
        {
            "name": "hydrate",
            "interval_minutes": 45,
            "message": "喝点水补充能量！",
            "enabled": True,
        },
    ],
}

DEFAULT_STATE: Dict[str, Any] = {
    "mood": 5,
    "affection": 0,
    "last_interaction": None,
}


def _ensure_app_directory() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ConfigManager:
    """Load and persist configuration data."""

    path: Path = CONFIG_FILE

    def load(self) -> Dict[str, Any]:
        _ensure_app_directory()
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return {**DEFAULT_CONFIG, **data}
        return copy.deepcopy(DEFAULT_CONFIG)

    def save(self, data: Dict[str, Any]) -> None:
        _ensure_app_directory()
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)


@dataclass
class StateManager:
    """Simple JSON backed storage for the pet state."""

    path: Path = STATE_FILE

    def load(self) -> Dict[str, Any]:
        _ensure_app_directory()
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return {**DEFAULT_STATE, **data}
        return copy.deepcopy(DEFAULT_STATE)

    def save(self, data: Dict[str, Any]) -> None:
        _ensure_app_directory()
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
