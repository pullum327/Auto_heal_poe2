"""螢幕區域擷取。"""

from __future__ import annotations

import numpy as np
import mss


class ScreenCapture:
    def __init__(self) -> None:
        self._sct = mss.mss()

    def grab_rect(self, x: int, y: int, w: int, h: int) -> np.ndarray:
        """擷取矩形區域，回傳 RGB uint8 array (h, w, 3)。"""
        if w <= 0 or h <= 0:
            return np.zeros((1, 1, 3), dtype=np.uint8)
        monitor = {"left": x, "top": y, "width": w, "height": h}
        shot = self._sct.grab(monitor)
        img = np.array(shot, dtype=np.uint8)
        # mss 回傳 BGRA
        return img[:, :, :3][:, :, ::-1]

    def grab_full_screen(self) -> tuple[np.ndarray, int, int]:
        """擷取主螢幕全畫面，回傳 (rgb, offset_x, offset_y)。"""
        mon = self._sct.monitors[1]
        shot = self._sct.grab(mon)
        img = np.array(shot, dtype=np.uint8)[:, :, :3][:, :, ::-1]
        return img, mon["left"], mon["top"]
