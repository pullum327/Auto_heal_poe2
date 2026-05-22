"""點擊球心校正覆蓋層。"""

from __future__ import annotations

from typing import Callable, Literal

import mss
import numpy as np
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QGuiApplication
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton

from core.orb_detector import _rgb_to_hsv
from core.screen_coords import (
    bounds_at_qt_point,
    orb_rect_from_center,
    physical_rect_to_qt,
    primary_monitor_physical_bounds,
    qt_global_to_physical,
    radius_from_percent,
)
from ui.styles import CALIB_OVERLAY_BTN, CALIB_HINT_LIFE, CALIB_HINT_MANA


def _sample_color_at(cx: int, cy: int) -> tuple[float, float, float] | None:
    try:
        with mss.mss() as sct:
            shot = sct.grab({"left": cx, "top": cy, "width": 1, "height": 1})
            px = np.array(shot, dtype=np.uint8)[0, 0, :3][::-1].astype(np.float64)
            hsv = _rgb_to_hsv(px.reshape(1, 3))[0]
            return float(hsv[0]), float(hsv[1]), float(hsv[2])
    except Exception:
        return None


def _color_warning(orb_type: Literal["life", "mana"], hsv: tuple[float, float, float]) -> str:
    h, s, v = hsv
    if s < 0.15 or v < 0.1:
        return ""
    if orb_type == "life":
        is_life = (h < 35 or h > 330) and s > 0.2
        if not is_life and 90 < h < 150:
            return "提示：此處偏藍，似乎不是生命球"
    else:
        is_mana = 90 < h < 150 and s > 0.15
        if not is_mana and (h < 35 or h > 330):
            return "提示：此處偏紅，似乎不是魔力球"
    return ""


class ClickCalibrationOverlay(QWidget):
    def __init__(
        self,
        orb_type: Literal["life", "mana"],
        title: str,
        radius_percent: float,
        on_done: Callable[[tuple[int, int, int, int] | None], None],
    ) -> None:
        super().__init__()
        self._orb_type = orb_type
        self._on_done = on_done
        self._title = title
        self._radius_percent = radius_percent
        self._bounds = primary_monitor_physical_bounds()
        self._radius_px = radius_from_percent(radius_percent, self._bounds)
        self._center: tuple[int, int] | None = None
        self._preview_rect: tuple[int, int, int, int] | None = None
        self._preview_qt: QRect | None = None
        self._warning = ""
        self._accent = QColor(229, 57, 53) if orb_type == "life" else QColor(33, 150, 243)

        virtual = QRect()
        for scr in QGuiApplication.screens():
            virtual = virtual.united(scr.geometry())
        if virtual.isValid():
            self.setGeometry(virtual)
        else:
            self.setGeometry(0, 0, 1920, 1080)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self._hint = QLabel(self._hint_text())
        self._hint.setStyleSheet(
            CALIB_HINT_LIFE if orb_type == "life" else CALIB_HINT_MANA
        )
        self._hint.setFont(QFont("Microsoft JhengHei", 11))
        self._hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(self._hint, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        confirm = QPushButton("確認  Enter")
        cancel = QPushButton("取消  Esc")
        cancel.setObjectName("calCancelBtn")
        for b in (confirm, cancel):
            b.setStyleSheet(CALIB_OVERLAY_BTN)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm.clicked.connect(self._confirm)
        cancel.clicked.connect(lambda: self._finish(None))
        btn_row.addStretch()
        btn_row.addWidget(cancel)
        btn_row.addWidget(confirm)
        layout.addLayout(btn_row)

    def _hint_text(self, extra: str = "") -> str:
        orb_name = "生命球（紅）" if self._orb_type == "life" else "魔力球（藍）"
        base = (
            f"{self._title}\n"
            f"點擊 {orb_name} 液體中心 · 滾輪調整大小 · Enter 確認 · Esc 取消"
        )
        if extra:
            return base + "\n" + extra
        return base

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 140))

        if self._preview_qt and self._preview_qt.width() > 2:
            r = self._preview_qt
            pen = QPen(self._accent, 3, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(QColor(self._accent.red(), self._accent.green(), self._accent.blue(), 45))
            painter.drawRect(r)

            cx = r.center().x()
            cy = r.center().y()
            cross = QPen(QColor(255, 255, 255, 200), 1, Qt.PenStyle.DashLine)
            painter.setPen(cross)
            painter.drawLine(cx - 12, cy, cx + 12, cy)
            painter.drawLine(cx, cy - 12, cx, cy + 12)

            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.drawText(
                r.topLeft() + QPoint(6, -10),
                f"{r.width()} × {r.height()} px",
            )

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._bounds = bounds_at_qt_point(event.globalPosition())
        self._radius_px = radius_from_percent(self._radius_percent, self._bounds)
        cx, cy = qt_global_to_physical(event.globalPosition())
        self._center = (cx, cy)
        self._update_preview()

        hsv = _sample_color_at(cx, cy)
        self._warning = _color_warning(self._orb_type, hsv) if hsv else ""
        extra = f"半徑 {self._radius_percent:.1f}%（{self._radius_px} px）"
        if self._warning:
            extra += f"\n{self._warning}"
        self._hint.setText(self._hint_text(extra))
        self.update()

    def wheelEvent(self, event) -> None:
        delta = event.angleDelta().y()
        step = 0.5 if delta > 0 else -0.5
        self._radius_percent = max(5.0, min(12.0, self._radius_percent + step))
        self._radius_px = radius_from_percent(self._radius_percent, self._bounds)
        if self._center:
            self._update_preview()
            extra = f"半徑 {self._radius_percent:.1f}%（{self._radius_px} px）"
            if self._warning:
                extra += f"\n{self._warning}"
            self._hint.setText(self._hint_text(extra))
            self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._confirm()
        elif event.key() == Qt.Key.Key_Escape:
            self._finish(None)
        else:
            super().keyPressEvent(event)

    def _update_preview(self) -> None:
        if self._center is None:
            return
        cx, cy = self._center
        self._preview_rect = orb_rect_from_center(cx, cy, self._radius_px, self._bounds)
        self._preview_qt = physical_rect_to_qt(self._preview_rect, self._bounds)

    def _confirm(self) -> None:
        if self._preview_rect is None:
            self._hint.setText(self._hint_text("請先點擊球體中心"))
            return
        self._finish(self._preview_rect)

    def _finish(self, rect: tuple[int, int, int, int] | None) -> None:
        self._on_done(rect)
        self.close()


def run_calibration(
    orb_type: Literal["life", "mana"],
    orb_label: str,
    radius_percent: float,
    on_complete: Callable[[tuple[int, int, int, int] | None], None],
) -> None:
    overlay = ClickCalibrationOverlay(orb_type, orb_label, radius_percent, on_complete)
    overlay.showFullScreen()
    overlay.raise_()
    overlay.activateWindow()
