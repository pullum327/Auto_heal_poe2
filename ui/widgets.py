"""共用 UI 元件。"""

from __future__ import annotations

from typing import Literal

from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QLinearGradient
from PyQt6.QtWidgets import QLabel, QPushButton, QWidget

from ui.styles import PILL_HEAL_ON, PILL_MANA_ON, PILL_OFF


class PillToggle(QPushButton):
    toggled_state = pyqtSignal(bool)

    def __init__(
        self,
        label: str,
        variant: Literal["heal", "mana"],
        active: bool = False,
    ) -> None:
        super().__init__()
        self._label = label
        self._variant = variant
        self._active = active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._toggle)
        self._refresh()

    def is_active(self) -> bool:
        return self._active

    def set_active(self, active: bool) -> None:
        self._active = active
        self._refresh()

    def _toggle(self) -> None:
        self._active = not self._active
        self._refresh()
        self.toggled_state.emit(self._active)

    def _refresh(self) -> None:
        if self._active:
            style = PILL_HEAL_ON if self._variant == "heal" else PILL_MANA_ON
            self.setText(f"{self._label}  ON")
        else:
            self.setText(f"{self._label}  OFF")
            style = PILL_OFF
        self.setStyleSheet(style)


class KeyCaptureButton(QPushButton):
    def __init__(self, label: str = "點擊錄製") -> None:
        super().__init__(label)
        self.setObjectName("keyCaptureBtn")
        self.setProperty("capturing", False)
        self._capturing = False
        self._key = ""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._start_capture)

    def key(self) -> str:
        return self._key

    def set_key(self, key: str) -> None:
        self._key = key
        self._set_capturing(False)
        self.setText(key.upper() if key else "點擊錄製")

    def _set_capturing(self, on: bool) -> None:
        self._capturing = on
        self.setProperty("capturing", on)
        self.style().unpolish(self)
        self.style().polish(self)

    def _start_capture(self) -> None:
        self._set_capturing(True)
        self.setText("請按下按鍵…")
        self.setFocus()

    def keyPressEvent(self, event) -> None:
        if not self._capturing:
            super().keyPressEvent(event)
            return
        key = event.key()
        text = event.text()
        if key == Qt.Key.Key_Escape:
            self.set_key(self._key)
            return
        if text and len(text) == 1:
            self._key = text.lower()
        else:
            key_map = {
                Qt.Key.Key_F1: "f1",
                Qt.Key.Key_F2: "f2",
                Qt.Key.Key_F3: "f3",
                Qt.Key.Key_F4: "f4",
                Qt.Key.Key_F5: "f5",
                Qt.Key.Key_F6: "f6",
                Qt.Key.Key_F7: "f7",
                Qt.Key.Key_F8: "f8",
                Qt.Key.Key_F9: "f9",
                Qt.Key.Key_F10: "f10",
                Qt.Key.Key_F11: "f11",
                Qt.Key.Key_F12: "f12",
            }
            self._key = key_map.get(key, "")
        self._set_capturing(False)
        self.setText(self._key.upper() if self._key else "點擊錄製")


class StatusDot(QWidget):
    """LED 風格狀態燈：運行（青綠）/ 暫停（琥珀）。"""

    _RUN = "run"
    _PAUSE = "pause"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = self._RUN
        self.setFixedSize(12, 12)
        self.setToolTip("運行中")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_running(self) -> None:
        self._state = self._RUN
        self.setToolTip("運行中")
        self.update()

    def set_paused(self) -> None:
        self._state = self._PAUSE
        self.setToolTip("已暫停（F8 恢復）")
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2.0
        cy = self.height() / 2.0
        core_r = 4.0

        if self._state == self._RUN:
            glow = QColor(76, 175, 80, 70)
            core_top = QColor(165, 245, 175)
            core_bot = QColor(56, 142, 60)
            ring = QColor(200, 255, 210, 180)
        else:
            glow = QColor(255, 152, 0, 65)
            core_top = QColor(255, 224, 178)
            core_bot = QColor(230, 120, 30)
            ring = QColor(255, 210, 150, 170)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QPointF(cx, cy), core_r + 3.5, core_r + 3.5)

        grad = QLinearGradient(cx, cy - core_r, cx, cy + core_r)
        grad.setColorAt(0, core_top)
        grad.setColorAt(1, core_bot)
        painter.setBrush(grad)
        painter.drawEllipse(QPointF(cx, cy), core_r, core_r)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(ring, 1.2))
        painter.drawEllipse(QPointF(cx, cy), core_r - 0.3, core_r - 0.3)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 140))
        painter.drawEllipse(QPointF(cx - 1.2, cy - 1.5), 1.6, 1.6)


def ui_font(size: int = 10, bold: bool = False) -> QFont:
    f = QFont("Microsoft JhengHei", size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    return f
