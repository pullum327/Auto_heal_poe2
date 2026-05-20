"""Qt 座標與螢幕實體像素（mss）轉換。"""

from __future__ import annotations

from PyQt6.QtCore import QPoint, QPointF, QRect
from PyQt6.QtGui import QGuiApplication


def _screen_physical_bounds(screen) -> tuple[int, int, int, int]:
    geo = screen.geometry()
    dpr = screen.devicePixelRatio()
    return (
        int(geo.x() * dpr),
        int(geo.y() * dpr),
        int(geo.width() * dpr),
        int(geo.height() * dpr),
    )


def primary_monitor_physical_bounds() -> tuple[int, int, int, int]:
    """主螢幕實體像素邊界 (left, top, width, height)。"""
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        return 0, 0, 1920, 1080
    return _screen_physical_bounds(screen)


def bounds_at_qt_point(point: QPointF | QPoint) -> tuple[int, int, int, int]:
    """點擊位置所在螢幕的實體像素邊界。"""
    screen = QGuiApplication.screenAt(
        point.toPoint() if isinstance(point, QPointF) else point
    )
    if screen is None:
        return primary_monitor_physical_bounds()
    return _screen_physical_bounds(screen)


def qt_global_to_physical(point: QPointF | QPoint) -> tuple[int, int]:
    """將 Qt 全域座標轉為 mss 使用的實體像素座標。"""
    screen = QGuiApplication.screenAt(point.toPoint())
    if screen is None:
        screen = QGuiApplication.primaryScreen()
    if screen is None:
        return int(point.x()), int(point.y())

    geo = screen.geometry()
    dpr = screen.devicePixelRatio()
    local_x = point.x() - geo.x()
    local_y = point.y() - geo.y()
    phys_x = int(geo.x() * dpr + local_x * dpr)
    phys_y = int(geo.y() * dpr + local_y * dpr)
    return phys_x, phys_y


def radius_from_percent(
    percent: float,
    bounds: tuple[int, int, int, int] | None = None,
) -> int:
    """依螢幕高度百分比計算球體半徑（實體像素）。"""
    if bounds is None:
        bounds = primary_monitor_physical_bounds()
    _, _, _, h = bounds
    return max(20, int(h * percent / 100.0))


def orb_rect_from_center(
    cx: int,
    cy: int,
    radius_px: int,
    bounds: tuple[int, int, int, int] | None = None,
) -> tuple[int, int, int, int]:
    """由球心與半徑產生正方形區域，並限制在螢幕範圍內。"""
    if bounds is None:
        bounds = primary_monitor_physical_bounds()
    left, top, width, height = bounds
    right = left + width
    bottom = top + height

    x = cx - radius_px
    y = cy - radius_px
    size = radius_px * 2

    if x < left:
        x = left
    if y < top:
        y = top
    if x + size > right:
        x = max(left, right - size)
    if y + size > bottom:
        y = max(top, bottom - size)

    w = min(size, right - x)
    h = min(size, bottom - y)
    return int(x), int(y), max(10, int(w)), max(10, int(h))


def physical_rect_to_qt(
    rect: tuple[int, int, int, int],
    bounds: tuple[int, int, int, int] | None = None,
) -> QRect:
    """實體像素矩形轉為 Qt 邏輯座標（用於預覽框繪製）。"""
    x, y, w, h = rect
    if bounds is None:
        bounds = primary_monitor_physical_bounds()
    bl, bt, _, _ = bounds
    screen = QGuiApplication.primaryScreen()
    for s in QGuiApplication.screens():
        sb = _screen_physical_bounds(s)
        if sb[0] == bl and sb[1] == bt:
            screen = s
            break
    if screen is None:
        return QRect(x, y, w, h)
    geo = screen.geometry()
    dpr = screen.devicePixelRatio()
    qx = geo.x() + (x - bl) / dpr
    qy = geo.y() + (y - bt) / dpr
    return QRect(int(qx), int(qy), max(1, int(w / dpr)), max(1, int(h / dpr)))
