"""全螢幕框選球體校正。"""

from __future__ import annotations

from typing import Callable

import numpy as np
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton

from core.capture import ScreenCapture


def _numpy_rgb_to_pixmap(rgb: np.ndarray) -> QPixmap:
    """將 RGB numpy 陣列轉為 QPixmap（相容新版 numpy / PyQt6）。"""
    img = np.ascontiguousarray(rgb, dtype=np.uint8)
    h, w = img.shape[:2]
    bytes_per_line = 3 * w
    qimg = QImage(
        img.tobytes(),
        w,
        h,
        bytes_per_line,
        QImage.Format.Format_RGB888,
    )
    return QPixmap.fromImage(qimg)


class SelectionOverlay(QWidget):
    def __init__(
        self,
        screenshot: np.ndarray,
        offset_x: int,
        offset_y: int,
        title: str,
        on_done: Callable[[tuple[int, int, int, int] | None], None],
    ) -> None:
        super().__init__()
        self._offset_x = offset_x
        self._offset_y = offset_y
        self._on_done = on_done
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._selection: QRect | None = None

        h, w, _ = screenshot.shape
        self._pixmap = _numpy_rgb_to_pixmap(screenshot)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setGeometry(offset_x, offset_y, w, h)

        self.setMouseTracking(True)
        # 子元件不攔截拖曳（按鈕除外）
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        hint = QLabel(f"{title}：拖曳框選球體，Enter 確認 / Esc 取消")
        hint.setStyleSheet(
            "color: white; background: rgba(0,0,0,0.7); padding: 8px; border-radius: 6px;"
        )
        hint.setFont(QFont("Microsoft JhengHei", 11))
        hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        layout.addWidget(hint, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addStretch()

        btn_row = QHBoxLayout()
        confirm = QPushButton("確認")
        cancel = QPushButton("取消")
        for b in (confirm, cancel):
            b.setStyleSheet(
                "QPushButton { background: #3d5afe; color: white; padding: 8px 16px;"
                " border-radius: 6px; }"
                "QPushButton:hover { background: #536dfe; }"
            )
        confirm.clicked.connect(self._confirm)
        cancel.clicked.connect(lambda: self._finish(None))
        btn_row.addStretch()
        btn_row.addWidget(confirm)
        btn_row.addWidget(cancel)
        layout.addLayout(btn_row)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))

        if self._selection and self._selection.width() > 2 and self._selection.height() > 2:
            painter.setPen(QPen(QColor(61, 90, 254), 2, Qt.PenStyle.SolidLine))
            painter.setBrush(QColor(61, 90, 254, 40))
            painter.drawRect(self._selection)
            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.drawText(
                self._selection.topLeft() + QPoint(4, -6),
                f"{self._selection.width()}×{self._selection.height()}",
            )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin = event.position().toPoint()
            self._current = self._origin
            self._selection = QRect(self._origin, self._current)
            self.update()

    def mouseMoveEvent(self, event) -> None:
        if self._origin is not None:
            self._current = event.position().toPoint()
            self._selection = QRect(self._origin, self._current).normalized()
            self.update()

    def mouseReleaseEvent(self, event) -> None:
        if self._origin is not None:
            self._current = event.position().toPoint()
            self._selection = QRect(self._origin, self._current).normalized()
            self._origin = None
            self.update()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self._confirm()
        elif event.key() == Qt.Key.Key_Escape:
            self._finish(None)
        else:
            super().keyPressEvent(event)

    def _confirm(self) -> None:
        if not self._selection or self._selection.width() < 5 or self._selection.height() < 5:
            self._finish(None)
            return
        r = self._selection
        rect = (
            r.x() + self._offset_x,
            r.y() + self._offset_y,
            r.width(),
            r.height(),
        )
        self._finish(rect)

    def _finish(self, rect: tuple[int, int, int, int] | None) -> None:
        self._on_done(rect)
        self.close()


def run_calibration(
    orb_label: str,
    on_complete: Callable[[tuple[int, int, int, int] | None], None],
) -> None:
    capture = ScreenCapture()
    img, ox, oy = capture.grab_full_screen()
    overlay = SelectionOverlay(img, ox, oy, orb_label, on_complete)
    overlay.showFullScreen()
