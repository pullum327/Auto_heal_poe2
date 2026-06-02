"""OrbDetector 單元測試（合成影像）。"""

import unittest

import numpy as np

from core.orb_detector import OrbDetector


class TestOrbDetector(unittest.TestCase):
    def _detector(self, orb_type: str = "life") -> OrbDetector:
        return OrbDetector(orb_type)

    def test_full_red_orb_high_fill(self) -> None:
        d = self._detector("life")
        img = np.zeros((120, 120, 3), dtype=np.uint8)
        img[:, :] = (200, 40, 30)
        fill = d._compute_fill(img)
        self.assertGreater(fill, 90.0)

    def test_dark_orb_low_fill(self) -> None:
        d = self._detector("life")
        img = np.zeros((120, 120, 3), dtype=np.uint8) + 25
        fill = d._compute_fill(img)
        self.assertLess(fill, 15.0)

    def test_half_orb_mid_fill(self) -> None:
        d = self._detector("mana")
        img = np.zeros((120, 120, 3), dtype=np.uint8) + 25
        img[60:, :, :] = (30, 80, 200)
        fill = d._compute_fill(img)
        self.assertGreater(fill, 35.0)
        self.assertLess(fill, 75.0)

    def test_gray_empty_ring_low_fill(self) -> None:
        """上半灰透明空槽 + 底部紅液體（低血情境）。"""
        d = self._detector("life")
        img = np.zeros((120, 120, 3), dtype=np.uint8)
        img[:68, :, :] = (85, 82, 88)
        img[68:, :, :] = (200, 45, 35)
        fill = d._compute_fill(img)
        self.assertLess(fill, 50.0)

    def test_ref_hsv_gray_not_counted_as_full(self) -> None:
        """有校正色時，灰色空槽不應被當成滿血。"""
        d = self._detector("life")
        d.set_reference_hsv((5.0, 0.75, 0.78))
        img = np.zeros((120, 120, 3), dtype=np.uint8)
        img[:, :] = (90, 86, 92)
        fill = d._compute_fill(img)
        self.assertLess(fill, 20.0)

    def test_ref_hsv_liquid_still_high_fill(self) -> None:
        d = self._detector("life")
        d.set_reference_hsv((5.0, 0.75, 0.78))
        img = np.zeros((120, 120, 3), dtype=np.uint8)
        img[:, :] = (200, 40, 30)
        fill = d._compute_fill(img)
        self.assertGreater(fill, 90.0)


if __name__ == "__main__":
    unittest.main()
