"""補瓶觸發邏輯：門檻、冷卻。"""

from __future__ import annotations

import time


class PotionController:
    def __init__(
        self,
        threshold: float = 45.0,
        cooldown: float = 1.0,
    ) -> None:
        self.threshold = threshold
        self.cooldown = cooldown
        self._last_fire = 0.0

    def update_settings(
        self,
        threshold: float | None = None,
        cooldown: float | None = None,
    ) -> None:
        if threshold is not None:
            self.threshold = threshold
        if cooldown is not None:
            self.cooldown = cooldown

    def should_fire(self, fill_percent: float) -> bool:
        if fill_percent <= 0:
            return False

        if fill_percent >= self.threshold:
            return False

        now = time.monotonic()
        if now - self._last_fire < self.cooldown:
            return False

        self._last_fire = now
        return True

    def reset(self) -> None:
        self._last_fire = 0.0
