"""背景輪詢執行緒：擷取、偵測、觸發補瓶。"""

from __future__ import annotations

import time
from typing import Any

from PyQt6.QtCore import QThread, pyqtSignal

from config import rect_from_config
from core.capture import ScreenCapture
from core.keyboard_sender import press_key
from core.orb_detector import OrbDetector
from core.potion_controller import PotionController


class PotionWorker(QThread):
    status_updated = pyqtSignal(float, float, bool, str)
    potion_fired = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._config: dict[str, Any] = {}
        self._running = True
        self._capture = ScreenCapture()
        self._life = OrbDetector("life", self._capture)
        self._mana = OrbDetector("mana", self._capture)
        self._heal_ctrl = PotionController()
        self._mana_ctrl = PotionController()

    def apply_config(self, config: dict[str, Any]) -> None:
        self._config = dict(config)
        life_rect = rect_from_config(config.get("life_orb_rect"))
        mana_rect = rect_from_config(config.get("mana_orb_rect"))
        self._life.set_rect(life_rect)
        self._mana.set_rect(mana_rect)

        life_ref = config.get("life_reference_hsv")
        mana_ref = config.get("mana_reference_hsv")
        self._life.set_reference_hsv(tuple(life_ref) if life_ref else None)
        self._mana.set_reference_hsv(tuple(mana_ref) if mana_ref else None)

        window = int(config.get("moving_average_window", 5))
        self._life.set_moving_average_window(window)
        self._mana.set_moving_average_window(window)

        self._heal_ctrl.update_settings(
            threshold=float(config.get("heal_threshold", 45)),
            cooldown=float(config.get("potion_cooldown", 1.0)),
        )
        self._mana_ctrl.update_settings(
            threshold=float(config.get("mana_threshold", 45)),
            cooldown=float(config.get("potion_cooldown", 1.0)),
        )

    def stop_worker(self) -> None:
        self._running = False

    def run(self) -> None:
        while self._running:
            interval = max(30, int(self._config.get("poll_interval_ms", 80))) / 1000.0
            cfg = self._config

            hp = self._life.read_fill_percent()
            mp = self._mana.read_fill_percent()

            anomaly = self._life.anomaly_detected or self._mana.anomaly_detected
            status_msg = ""
            if not self._life.is_calibrated or not self._mana.is_calibrated:
                status_msg = "請校正球體"
            elif anomaly:
                status_msg = "偵測異常"

            hp_val = hp if hp is not None else -1.0
            mp_val = mp if mp is not None else -1.0
            self.status_updated.emit(hp_val, mp_val, anomaly, status_msg)

            master = bool(cfg.get("master_enabled", False))
            can_act = master and not anomaly and status_msg == ""

            if can_act and bool(cfg.get("heal_enabled", True)) and hp is not None:
                if self._heal_ctrl.should_fire(hp):
                    key = str(cfg.get("heal_key", "1"))
                    press_key(key)
                    self.potion_fired.emit("heal")

            if can_act and bool(cfg.get("mana_enabled", True)) and mp is not None:
                if self._mana_ctrl.should_fire(mp):
                    key = str(cfg.get("mana_key", "2"))
                    press_key(key)
                    self.potion_fired.emit("mana")

            time.sleep(interval)
