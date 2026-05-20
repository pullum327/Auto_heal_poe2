"""球體填充比例偵測。"""

from __future__ import annotations

from collections import deque

import numpy as np

from core.capture import ScreenCapture


def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """rgb: (N, 3) float 0-255 -> hsv (N, 3) h:0-360, s,v:0-1"""
    r, g, b = rgb[:, 0] / 255.0, rgb[:, 1] / 255.0, rgb[:, 2] / 255.0
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin
    h = np.zeros_like(cmax)
    mask = delta > 1e-6
    rc = np.zeros_like(cmax)
    gc = np.zeros_like(cmax)
    bc = np.zeros_like(cmax)
    rc[mask] = ((g - b) / delta)[mask]
    gc[mask] = ((b - r) / delta + 2.0)[mask]
    bc[mask] = ((r - g) / delta + 4.0)[mask]
    idx_r = mask & (cmax == r)
    idx_g = mask & (cmax == g)
    idx_b = mask & (cmax == b)
    h[idx_r] = (rc[idx_r] % 6.0) * 60.0
    h[idx_g] = gc[idx_g] * 60.0
    h[idx_b] = bc[idx_b] * 60.0
    s = np.where(cmax > 1e-6, delta / cmax, 0.0)
    v = cmax
    return np.stack([h, s, v], axis=1)


class OrbDetector:
    """從球體矩形區域估算填充百分比。"""

    SAMPLE_COUNT = 50
    ANOMALY_THRESHOLD = 10

    def __init__(
        self,
        orb_type: str,
        capture: ScreenCapture | None = None,
    ) -> None:
        self.orb_type = orb_type  # "life" | "mana"
        self.capture = capture or ScreenCapture()
        self._rect: tuple[int, int, int, int] | None = None
        self._ref_hsv: tuple[float, float, float] | None = None
        self._history: deque[float] = deque(maxlen=5)
        self._anomaly_count = 0
        self._last_raw: float | None = None

    def set_rect(self, rect: tuple[int, int, int, int] | None) -> None:
        self._rect = rect

    def set_reference_hsv(self, hsv: tuple[float, float, float] | None) -> None:
        self._ref_hsv = hsv

    def set_moving_average_window(self, window: int) -> None:
        self._history = deque(self._history, maxlen=max(1, window))

    @property
    def is_calibrated(self) -> bool:
        return self._rect is not None

    @property
    def anomaly_detected(self) -> bool:
        return self._anomaly_count >= self.ANOMALY_THRESHOLD

    def read_fill_percent(self) -> float | None:
        if self._rect is None:
            return None
        x, y, w, h = self._rect
        try:
            img = self.capture.grab_rect(x, y, w, h)
        except Exception:
            self._register_anomaly()
            return self._smoothed()

        if img.size == 0:
            self._register_anomaly()
            return self._smoothed()

        raw = self._compute_fill(img)
        self._last_raw = raw

        if self._is_frame_anomaly(img, raw):
            self._anomaly_count += 1
        else:
            self._anomaly_count = 0

        self._history.append(raw)
        return self._smoothed()

    def capture_reference_from_rect(self) -> tuple[float, float, float] | None:
        """從球體中心區域取樣作為參考色（避開底部裝飾框）。"""
        if self._rect is None:
            return None
        x, y, w, h = self._rect
        try:
            img = self.capture.grab_rect(x, y, w, h)
        except Exception:
            return None
        if h < 2:
            return None
        cx, cy = w // 2, h // 2
        offsets = [(0, 0), (-2, 0), (2, 0), (0, -2), (0, 2)]
        pixels_list: list[np.ndarray] = []
        for dx, dy in offsets:
            px = cx + dx
            py = cy + dy
            if 0 <= px < w and 0 <= py < h:
                pixels_list.append(img[py, px, :].astype(np.float64))
        if not pixels_list:
            return None
        pixels = np.stack(pixels_list)
        hsv = _rgb_to_hsv(pixels)
        mean = hsv.mean(axis=0)
        return float(mean[0]), float(mean[1]), float(mean[2])

    def _smoothed(self) -> float | None:
        if not self._history:
            return self._last_raw
        return sum(self._history) / len(self._history)

    def _register_anomaly(self) -> None:
        self._anomaly_count += 1

    def _compute_fill(self, img: np.ndarray) -> float:
        h, w, _ = img.shape
        cx = w // 2
        cy_center = h / 2.0
        circle_r = min(w, h) / 2.0 * 0.85
        ys = np.linspace(h - 1, 0, self.SAMPLE_COUNT).astype(int)

        empty_flags: list[bool] = []
        valid_count = 0
        for y in ys:
            dy = y - cy_center
            if abs(dy) > circle_r:
                continue
            valid_count += 1
            pixel = img[y, cx, :].astype(np.float64)
            empty_flags.append(self._is_empty_black_pixel(pixel))

        if valid_count == 0 or not empty_flags:
            return 0.0

        empty_count = int(sum(empty_flags))
        empty_ratio = empty_count / valid_count
        return max(0.0, min(100.0, (1.0 - empty_ratio) * 100.0))

    def _is_empty_black_pixel(self, rgb: np.ndarray) -> bool:
        r, g, b = float(rgb[0]), float(rgb[1]), float(rgb[2])
        peak = max(r, g, b)
        if peak <= 38:
            return True

        hsv = _rgb_to_hsv(rgb.reshape(1, 3))[0]
        h, s, v = float(hsv[0]), float(hsv[1]), float(hsv[2])
        _ = h

        if v <= 0.2 and s <= 0.38:
            return True
        if v <= 0.15:
            return True
        return v <= 0.28 and s <= 0.18 and peak <= 58


    def _is_frame_anomaly(self, img: np.ndarray, fill: float) -> bool:
        mean = img.mean()
        std = img.std()
        if mean < 5 and std < 3:
            return True
        if std < 2 and (fill <= 0.5 or fill >= 99.5):
            return True
        return False
