"""設定檔讀寫與預設值。"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


def app_dir() -> Path:
    """開發模式：專案目錄；打包後：exe 所在目錄。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


CONFIG_PATH = app_dir() / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "heal_key": "1",
    "mana_key": "2",
    "heal_threshold": 45,
    "mana_threshold": 45,
    "heal_hysteresis": 10,  # 已廢棄，保留以相容舊 config.json
    "mana_hysteresis": 10,
    "potion_cooldown": 1.0,
    "poll_interval_ms": 80,
    "moving_average_window": 5,
    "hotkey_heal_toggle": "f6",
    "hotkey_mana_toggle": "f7",
    "hotkey_master_toggle": "f8",
    "master_enabled": True,
    "heal_enabled": True,
    "mana_enabled": True,
    "life_orb_rect": None,
    "mana_orb_rect": None,
    "life_reference_hsv": None,
    "mana_reference_hsv": None,
    "overlay_x": 100,
    "overlay_y": 100,
    "orb_radius_percent": 7.5,
}


def default_config() -> dict[str, Any]:
    return deepcopy(DEFAULT_CONFIG)


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        cfg = default_config()
        save_config(cfg)
        return cfg
    with CONFIG_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    merged = default_config()
    merged.update(data)
    return merged


def save_config(config: dict[str, Any]) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def rect_from_config(value: list[int] | None) -> tuple[int, int, int, int] | None:
    if not value or len(value) != 4:
        return None
    return tuple(value)


def rect_to_config(rect: tuple[int, int, int, int] | None) -> list[int] | None:
    if rect is None:
        return None
    return list(rect)
