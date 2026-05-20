"""遊戲按鍵模擬封裝。"""

from __future__ import annotations

import pydirectinput

# 避免 pydirectinput 預設延遲過長
pydirectinput.PAUSE = 0.02


def press_key(key: str) -> None:
    if not key:
        return
    pydirectinput.press(key.lower())


def normalize_key_name(key: str) -> str:
    k = key.strip().lower()
    aliases = {
        "return": "enter",
        "escape": "esc",
    }
    return aliases.get(k, k)
