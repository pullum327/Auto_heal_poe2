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
        """從球體底部取樣作為滿填充參考色。"""
        if self._rect is None:
            return None
        x, y, w, h = self._rect
        try:
            img = self.capture.grab_rect(x, y, w, h)
        except Exception:
            return None
        if h < 2:
            return None
        cx = w // 2
        bottom_rows = img[max(0, h - 3) : h, cx : cx + 1, :]
        if bottom_rows.size == 0:
            return None
        pixels = bottom_rows.reshape(-1, 3).astype(np.float64)
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
        ys = np.linspace(h - 1, 0, self.SAMPLE_COUNT).astype(int)
        pixels = img[ys, cx, :].astype(np.float64)
        filled = np.array([self._is_filled_pixel(p) for p in pixels])

        top_filled = 0
        for i, is_fill in enumerate(filled):
            if is_fill:
                top_filled = i
            else:
                break
        if not filled.any():
            return 0.0
        return (top_filled + 1) / self.SAMPLE_COUNT * 100.0

    def _is_filled_pixel(self, rgb: np.ndarray) -> bool:
        hsv = _rgb_to_hsv(rgb.reshape(1, 3))[0]
        h, s, v = float(hsv[0]), float(hsv[1]), float(hsv[2])

        if self._ref_hsv is not None:
            rh, rs, rv = self._ref_hsv
            dh = min(abs(h - rh), 360 - abs(h - rh))
            if dh < 25 and abs(s - rs) < 0.35 and abs(v - rv) < 0.35:
                return True
            if s > 0.25 and v > 0.2 and dh < 40:
                return True

        if self.orb_type == "life":
            return (h < 35 or h > 330) and s > 0.25 and v > 0.2
        return 90 < h < 150 and s > 0.2 and v > 0.15

    def _is_frame_anomaly(self, img: np.ndarray, fill: float) -> bool:
        mean = img.mean()
        std = img.std()
        if mean < 5 and std < 3:
            return True
        if std < 2 and (fill <= 0.5 or fill >= 99.5):
            return True
        return False
