"""設定對話框 — 玻璃擬態（高不透明面板 + 外陰影，拖曳與主浮層一致）。"""

from __future__ import annotations

from typing import Any, Callable, Literal

from PyQt6.QtCore import QEvent, QPoint, Qt
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QDoubleSpinBox,
    QSpinBox,
    QFormLayout,
    QWidget,
    QScrollArea,
    QFrame,
    QAbstractButton,
    QAbstractSpinBox,
    QScrollBar,
)

from ui.styles import (
    SETTINGS_BORDER_INNER,
    SETTINGS_BORDER_OUTER,
    SETTINGS_GRADIENT_BOTTOM,
    SETTINGS_GRADIENT_MID,
    SETTINGS_GRADIENT_TOP,
    SETTINGS_HIGHLIGHT_TOP,
    SETTINGS_PANEL_RADIUS,
    glass_dialog_stylesheet,
    glass_dialog_panel_stylesheet,
    SETTINGS_HEADER_BTN,
)
from ui.widgets import KeyCaptureButton, ui_font

_HEADER_BTN_SIZE = 30


class SettingsPanel(QFrame):
    """自繪高不透明玻璃面板（子元件維持實色底，避免穿透遊戲）。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAutoFillBackground(False)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(1, 1, -1, -1)
        radius = SETTINGS_PANEL_RADIUS

        grad = QLinearGradient(0, r.top(), 0, r.bottom())
        grad.setColorAt(0.0, QColor(*SETTINGS_GRADIENT_TOP))
        grad.setColorAt(0.42, QColor(*SETTINGS_GRADIENT_MID))
        grad.setColorAt(1.0, QColor(*SETTINGS_GRADIENT_BOTTOM))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawRoundedRect(r, radius, radius)

        highlight = QLinearGradient(0, r.top(), 0, r.top() + 56)
        highlight.setColorAt(0.0, QColor(*SETTINGS_HIGHLIGHT_TOP))
        highlight.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(highlight)
        painter.drawRoundedRect(r, radius, radius)

        painter.setPen(QPen(QColor(*SETTINGS_BORDER_OUTER), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(r, radius, radius)

        painter.setPen(QPen(QColor(*SETTINGS_BORDER_INNER), 1))
        inner = r.adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(inner, radius - 2, radius - 2)

        super().paintEvent(event)


class SettingsDialog(QDialog):
    def __init__(
        self,
        config: dict[str, Any],
        on_save: Callable[[dict[str, Any]], None],
        on_calibrate_life: Callable[[], None],
        on_calibrate_mana: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._config = dict(config)
        self._on_save = on_save
        self._on_calibrate_life = on_calibrate_life
        self._on_calibrate_mana = on_calibrate_mana
        self._drag_pos: QPoint | None = None

        self.setWindowTitle("POE2 自動補瓶 — 設定")
        self.setMinimumSize(456, 540)
        self.resize(476, 600)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Dialog,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(glass_dialog_stylesheet())
        self.setFont(ui_font(10))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        self._panel = SettingsPanel()
        self._panel.setObjectName("glassDialogPanel")
        self._panel.setStyleSheet(glass_dialog_panel_stylesheet())
        outer.addWidget(self._panel)

        root = QVBoxLayout(self._panel)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("設定")
        title.setObjectName("dialogTitle")
        title.setFont(ui_font(16, bold=True))
        close_btn = QPushButton("✕")
        close_btn.setObjectName("headerCloseBtn")
        close_btn.setFixedSize(_HEADER_BTN_SIZE, _HEADER_BTN_SIZE)
        close_btn.setStyleSheet(SETTINGS_HEADER_BTN)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("關閉")
        close_btn.clicked.connect(self.reject)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        root.addLayout(header)

        header_divider = QFrame()
        header_divider.setObjectName("settingsHeaderDivider")
        header_divider.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(header_divider)

        scroll = QScrollArea()
        scroll.setObjectName("settingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setObjectName("settingsScrollContent")
        layout = QVBoxLayout(content)
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 8, 4)

        potion_section = self._settings_section()
        potion_layout = QVBoxLayout(potion_section)
        potion_layout.setContentsMargins(14, 14, 14, 14)
        potion_layout.setSpacing(12)

        keys_form = QFormLayout()
        keys_form.setSpacing(10)
        self.heal_key_btn = KeyCaptureButton()
        self.heal_key_btn.set_key(str(config.get("heal_key", "1")))
        self.mana_key_btn = KeyCaptureButton()
        self.mana_key_btn.set_key(str(config.get("mana_key", "2")))
        keys_form.addRow(self._form_label("補血鍵"), self.heal_key_btn)
        keys_form.addRow(self._form_label("補魔鍵"), self.mana_key_btn)
        potion_layout.addLayout(keys_form)

        self.heal_slider, self.heal_label = self._make_slider(
            int(config.get("heal_threshold", 45)), "補血", "life"
        )
        self.mana_slider, self.mana_label = self._make_slider(
            int(config.get("mana_threshold", 45)), "補魔", "mana"
        )
        potion_layout.addWidget(self.heal_label)
        potion_layout.addWidget(self.heal_slider)
        potion_layout.addWidget(self.mana_label)
        potion_layout.addWidget(self.mana_slider)

        misc_form = QFormLayout()
        misc_form.setSpacing(10)
        self.cooldown_spin = QDoubleSpinBox()
        self.cooldown_spin.setRange(0.25, 3.0)
        self.cooldown_spin.setSingleStep(0.05)
        self.cooldown_spin.setDecimals(2)
        self.cooldown_spin.setValue(float(config.get("potion_cooldown", 1.0)))
        misc_form.addRow(self._form_label("藥水冷卻"), self.cooldown_spin)

        self.poll_spin = QSpinBox()
        self.poll_spin.setRange(30, 500)
        self.poll_spin.setSuffix(" ms")
        self.poll_spin.setValue(int(config.get("poll_interval_ms", 80)))
        misc_form.addRow(self._form_label("輪詢間隔"), self.poll_spin)

        self.avg_spin = QSpinBox()
        self.avg_spin.setRange(1, 15)
        self.avg_spin.setValue(int(config.get("moving_average_window", 5)))
        misc_form.addRow(self._form_label("移動平均"), self.avg_spin)
        potion_layout.addLayout(misc_form)
        layout.addWidget(potion_section)

        hotkey_section = self._settings_section()
        hotkey_form = QFormLayout(hotkey_section)
        hotkey_form.setContentsMargins(14, 14, 14, 14)
        hotkey_form.setSpacing(10)
        self.hotkey_heal_btn = KeyCaptureButton()
        self.hotkey_heal_btn.set_key(str(config.get("hotkey_heal_toggle", "f6")))
        self.hotkey_mana_btn = KeyCaptureButton()
        self.hotkey_mana_btn.set_key(str(config.get("hotkey_mana_toggle", "f7")))
        self.hotkey_master_btn = KeyCaptureButton()
        self.hotkey_master_btn.set_key(str(config.get("hotkey_master_toggle", "f8")))
        hotkey_form.addRow(self._form_label("補血開關"), self.hotkey_heal_btn)
        hotkey_form.addRow(self._form_label("補魔開關"), self.hotkey_mana_btn)
        hotkey_form.addRow(self._form_label("全域暫停"), self.hotkey_master_btn)
        layout.addWidget(hotkey_section)

        cal_section = self._settings_section()
        cal_form = QVBoxLayout(cal_section)
        cal_form.setContentsMargins(14, 14, 14, 14)
        cal_form.setSpacing(12)
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(5.0, 12.0)
        self.radius_spin.setSingleStep(0.5)
        self.radius_spin.setSuffix(" %")
        self.radius_spin.setValue(float(config.get("orb_radius_percent", 7.5)))
        radius_row = QHBoxLayout()
        radius_row.addWidget(self._form_label("球體半徑 %"))
        radius_row.addWidget(self.radius_spin)
        cal_form.addLayout(radius_row)

        cal_layout = QHBoxLayout()
        cal_layout.setSpacing(10)
        btn_life = QPushButton("校正生命球")
        btn_life.setObjectName("calLifeBtn")
        btn_mana = QPushButton("校正魔力球")
        btn_mana.setObjectName("calManaBtn")
        btn_life.clicked.connect(self._calibrate_life)
        btn_mana.clicked.connect(self._calibrate_mana)
        cal_layout.addWidget(btn_life)
        cal_layout.addWidget(btn_mana)
        cal_form.addLayout(cal_layout)
        layout.addWidget(cal_section)

        layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 4, 0, 0)
        btn_row.setSpacing(10)
        save_btn = QPushButton("儲存設定")
        save_btn.setObjectName("primaryBtn")
        cancel_btn = QPushButton("取消")
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

        self._attach_drag_handlers(self._panel)

    def paintEvent(self, event) -> None:
        """外緣柔和陰影（僅邊距區，不影響面板內可讀性）。"""
        if hasattr(self, "_panel"):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            base = self._panel.geometry()
            for spread, alpha in ((12, 22), (7, 32), (3, 44)):
                shadow = base.adjusted(-spread, -spread + 2, spread, spread + 4)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(72, 64, 108, alpha))
                painter.drawRoundedRect(
                    shadow,
                    SETTINGS_PANEL_RADIUS + spread // 2,
                    SETTINGS_PANEL_RADIUS + spread // 2,
                )
        super().paintEvent(event)

    def _attach_drag_handlers(self, root: QWidget) -> None:
        root.installEventFilter(self)
        for child in root.findChildren(QWidget):
            child.installEventFilter(self)

    @staticmethod
    def _is_interactive(widget: QWidget) -> bool:
        if isinstance(
            widget,
            (QAbstractButton, QSlider, QAbstractSpinBox, QScrollBar, KeyCaptureButton),
        ):
            return True
        return False

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            if (
                event.button() == Qt.MouseButton.LeftButton
                and not self._is_interactive(obj)
            ):
                self._drag_pos = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
        elif event.type() == QEvent.Type.MouseMove:
            if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                return True
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._drag_pos = None
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None

    @staticmethod
    def _settings_section() -> QFrame:
        section = QFrame()
        section.setObjectName("settingsSection")
        return section

    def _form_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("formLabel")
        return lbl

    def _make_slider(
        self, value: int, prefix: str, orb: Literal["life", "mana"]
    ) -> tuple[QSlider, QLabel]:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(10, 90)
        slider.setValue(value)
        label = QLabel(f"{prefix}  {value}%")
        label.setObjectName("thresholdLife" if orb == "life" else "thresholdMana")
        slider.valueChanged.connect(
            lambda v, p=prefix, lb=label: lb.setText(f"{p}  {v}%")
        )
        return slider, label

    def _calibrate_life(self) -> None:
        self._on_calibrate_life()

    def _calibrate_mana(self) -> None:
        self._on_calibrate_mana()

    def _save(self) -> None:
        self._config["heal_key"] = self.heal_key_btn.key() or "1"
        self._config["mana_key"] = self.mana_key_btn.key() or "2"
        self._config["heal_threshold"] = self.heal_slider.value()
        self._config["mana_threshold"] = self.mana_slider.value()
        self._config["potion_cooldown"] = self.cooldown_spin.value()
        self._config["poll_interval_ms"] = self.poll_spin.value()
        self._config["moving_average_window"] = self.avg_spin.value()
        self._config["orb_radius_percent"] = self.radius_spin.value()
        self._config["hotkey_heal_toggle"] = self.hotkey_heal_btn.key() or "f6"
        self._config["hotkey_mana_toggle"] = self.hotkey_mana_btn.key() or "f7"
        self._config["hotkey_master_toggle"] = self.hotkey_master_btn.key() or "f8"
        self._on_save(self._config)
        self.accept()
