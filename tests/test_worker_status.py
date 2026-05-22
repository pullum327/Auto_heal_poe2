"""worker 狀態訊息組合測試。"""

import unittest
from unittest.mock import MagicMock

from services.worker import _build_status


class TestBuildStatus(unittest.TestCase):
    def _mock_detector(self, calibrated: bool, anomaly: bool) -> MagicMock:
        d = MagicMock()
        d.is_calibrated = calibrated
        d.anomaly_detected = anomaly
        return d

    def test_heal_only_needs_life_calibration(self) -> None:
        cfg = {"heal_enabled": True, "mana_enabled": False}
        life = self._mock_detector(False, False)
        mana = self._mock_detector(False, False)
        msg, blocked = _build_status(cfg, life, mana)
        self.assertIn("生命球", msg)
        self.assertNotIn("魔力球", msg)
        self.assertTrue(blocked)

    def test_life_anomaly_does_not_block_mana_when_mana_enabled(self) -> None:
        cfg = {"heal_enabled": True, "mana_enabled": True}
        life = self._mock_detector(True, True)
        mana = self._mock_detector(True, False)
        msg, blocked = _build_status(cfg, life, mana)
        self.assertIn("生命球偵測異常", msg)
        self.assertNotIn("魔力球偵測異常", msg)
        self.assertTrue(blocked)


if __name__ == "__main__":
    unittest.main()
