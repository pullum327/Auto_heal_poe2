"""補瓶觸發邏輯：門檻、遲滯、冷卻。"""

from __future__ import annotations

import time


class PotionController:
    def __init__(
        self,
        threshold: float = 45.0,
        hysteresis: float = 10.0,
        cooldown: float = 1.0,
    ) -> None:
        self.threshold = threshold
        self.hysteresis = hysteresis
        self.cooldown = cooldown
        self._armed = True
        self._last_fire = 0.0

    def update_settings(
        self,
        threshold: float | None = None,
        hysteresis: float | None = None,
        cooldown: float | None = None,
    ) -> None:
        if threshold is not None:
            self.threshold = threshold
        if hysteresis is not None:
            self.hysteresis = hysteresis
        if cooldown is not None:
            self.cooldown = cooldown

    def should_fire(self, fill_percent: float) -> bool:
        release_level = min(100.0, self.threshold + self.hysteresis)

        if fill_percent >= release_level:
            self._armed = True

        if not self._armed:
            return False

        if fill_percent >= self.threshold:
            return False

        now = time.monotonic()
        if now - self._last_fire < self.cooldown:
            return False

        self._last_fire = now
        self._armed = False
        return True

    def reset(self) -> None:
        self._armed = True
        self._last_fire = 0.0
