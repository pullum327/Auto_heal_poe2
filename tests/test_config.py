"""config 工具函式測試。"""

import unittest

from config import rect_from_config, rect_to_config


class TestConfigRect(unittest.TestCase):
    def test_rect_from_config_valid(self) -> None:
        self.assertEqual(rect_from_config([10, 20, 30, 40]), (10, 20, 30, 40))

    def test_rect_from_config_invalid(self) -> None:
        self.assertIsNone(rect_from_config(None))
        self.assertIsNone(rect_from_config([1, 2]))
        self.assertIsNone(rect_from_config([]))

    def test_rect_to_config_roundtrip(self) -> None:
        r = (5, 6, 7, 8)
        self.assertEqual(rect_from_config(rect_to_config(r)), r)


if __name__ == "__main__":
    unittest.main()
