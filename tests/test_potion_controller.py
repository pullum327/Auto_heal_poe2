"""PotionController 單元測試。"""

import time
import unittest

from core.potion_controller import PotionController


class TestPotionController(unittest.TestCase):
    def test_no_fire_above_threshold(self) -> None:
        ctrl = PotionController(threshold=45.0, cooldown=0.1)
        self.assertFalse(ctrl.should_fire(50.0))

    def test_fire_below_threshold(self) -> None:
        ctrl = PotionController(threshold=45.0, cooldown=0.1)
        self.assertTrue(ctrl.should_fire(30.0))

    def test_cooldown_blocks_repeat(self) -> None:
        ctrl = PotionController(threshold=45.0, cooldown=0.5)
        self.assertTrue(ctrl.should_fire(20.0))
        self.assertFalse(ctrl.should_fire(20.0))
        time.sleep(0.55)
        self.assertTrue(ctrl.should_fire(20.0))


if __name__ == "__main__":
    unittest.main()
