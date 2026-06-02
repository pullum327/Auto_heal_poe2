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
    """從球體矩形區域估算填充百分比（空槽：黑圈 + 灰透明；液體色優先）。"""

    SAMPLE_COUNT = 60
    ANOMALY_THRESHOLD = 10
    SAMPLE_LINE_OFFSET_RATIO = 0.12

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

    def _sample_columns(self, w: int) -> list[int]:
        cx = w // 2
        offset = max(1, int(w * self.SAMPLE_LINE_OFFSET_RATIO))
        cols = [cx - offset, cx, cx + offset]
        return [max(0, min(w - 1, c)) for c in cols]

    def _compute_fill(self, img: np.ndarray) -> float:
        h, w, _ = img.shape
        cy_center = h / 2.0
        circle_r = min(w, h) / 2.0 * 0.85
        cols = self._sample_columns(w)
        ys = np.linspace(h - 1, 0, self.SAMPLE_COUNT).astype(int)

        empty_flags: list[bool] = []
        for y in ys:
            dy = y - cy_center
            if abs(dy) > circle_r:
                continue
            votes: list[bool] = []
            for col in cols:
                pixel = img[y, col, :].astype(np.float64)
                votes.append(self._is_sample_empty(pixel))
            empty_flags.append(sum(votes) >= 2)

        if not empty_flags:
            return 0.0

        empty_ratio = sum(empty_flags) / len(empty_flags)
        return max(0.0, min(100.0, (1.0 - empty_ratio) * 100.0))

    def _is_sample_empty(self, rgb: np.ndarray) -> bool:
        """單像素：液體優先，其次空槽規則，模糊預設為空。"""
        if self._is_liquid_pixel(rgb):
            return False
        if self._is_empty_pixel(rgb):
            return True
        return True

    def _pixel_hsv(self, rgb: np.ndarray) -> tuple[float, float, float]:
        hsv = _rgb_to_hsv(rgb.reshape(1, 3))[0]
        return float(hsv[0]), float(hsv[1]), float(hsv[2])

    def _is_liquid_pixel(self, rgb: np.ndarray) -> bool:
        r, g, b = float(rgb[0]), float(rgb[1]), float(rgb[2])
        if self._matches_rgb_dominance(r, g, b):
            return True
        h, s, v = self._pixel_hsv(rgb)
        if self._ref_hsv is not None and self._matches_reference_hsv(h, s, v):
            return True
        return self._matches_hsv_fallback(h, s, v)

    def _is_empty_pixel(self, rgb: np.ndarray) -> bool:
        if self._is_empty_black_pixel(rgb):
            return True
        if self._is_empty_gray_pixel(rgb):
            return True
        if self._ref_hsv is not None:
            h, s, v = self._pixel_hsv(rgb)
            if not self._matches_reference_hsv(h, s, v) and s < 0.25:
                return True
        return False

    def _is_empty_black_pixel(self, rgb: np.ndarray) -> bool:
        r, g, b = float(rgb[0]), float(rgb[1]), float(rgb[2])
        peak = max(r, g, b)
        if peak <= 38:
            return True

        _, s, v = self._pixel_hsv(rgb)

        if v <= 0.2 and s <= 0.38:
            return True
        if v <= 0.15:
            return True
        return v <= 0.28 and s <= 0.18 and peak <= 58

    def _is_empty_gray_pixel(self, rgb: np.ndarray) -> bool:
        """半透明／灰色空槽（非純黑）。"""
        r, g, b = float(rgb[0]), float(rgb[1]), float(rgb[2])
        peak = max(r, g, b)
        spread = peak - min(r, g, b)
        _, s, v = self._pixel_hsv(rgb)

        if spread < 40 and peak < 130:
            return True
        if s < 0.22 and 0.12 < v < 0.55 and spread < 45:
            return True
        if s < 0.18 and 0.12 < v < 0.48:
            return True
        return False

    def _matches_rgb_dominance(self, r: float, g: float, b: float) -> bool:
        if self.orb_type == "mana":
            if b > 50 and b > r * 1.05 and b >= g * 0.8:
                return True
            return b > 35 and (b - r) > 15
        if r > 50 and r > g * 1.05 and r > b * 1.05:
            return True
        return r > 35 and (r - g) > 15 and (r - b) > 15

    def _matches_reference_hsv(self, h: float, s: float, v: float) -> bool:
        rh, rs, rv = self._ref_hsv  # type: ignore[misc]
        dh = min(abs(h - rh), 360 - abs(h - rh))
        hue_tol = 55
        if dh < hue_tol and abs(s - rs) < 0.45 and abs(v - rv) < 0.45:
            return True
        return s > 0.12 and v > 0.12 and dh < hue_tol + 15

    def _matches_hsv_fallback(self, h: float, s: float, v: float) -> bool:
        if s < 0.08 or v < 0.12:
            return False
        if self.orb_type == "mana":
            return 70 < h < 270
        return h < 45 or h > 300

    def _is_frame_anomaly(self, img: np.ndarray, fill: float) -> bool:
        mean = img.mean()
        std = img.std()
        if mean < 5 and std < 3:
            return True
        if std < 2 and (fill <= 0.5 or fill >= 99.5):
            return True
        return False
