"""設定對話框 — 透明玻璃風格（拖曳方式與主浮層一致）。"""

from __future__ import annotations

from typing import Any, Callable, Literal

from PyQt6.QtCore import QEvent, QPoint, Qt
from PyQt6.QtGui import QColor, QPainter
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
    QGroupBox,
    QWidget,
    QScrollArea,
    QFrame,
    QAbstractButton,
    QAbstractSpinBox,
    QScrollBar,
)

from ui.styles import (
    glass_dialog_stylesheet,
    glass_dialog_panel_stylesheet,
    HEADER_ICON_BTN,
)
from ui.widgets import KeyCaptureButton, ui_font

_HEADER_BTN_SIZE = 30


class SettingsPanel(QFrame):
    """不透明玻璃面板（避免子元件透明穿透遊戲畫面）。"""

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(42, 30, 66))
        painter.drawRoundedRect(self.rect(), 20, 20)
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

        panel = SettingsPanel()
        panel.setObjectName("glassDialogPanel")
        panel.setStyleSheet(glass_dialog_panel_stylesheet())
        outer.addWidget(panel)

        root = QVBoxLayout(panel)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("設定")
        title.setObjectName("dialogTitle")
        title.setFont(ui_font(16, bold=True))
        close_btn = QPushButton("✕")
        close_btn.setObjectName("headerCloseBtn")
        close_btn.setFixedSize(_HEADER_BTN_SIZE, _HEADER_BTN_SIZE)
        close_btn.setStyleSheet(HEADER_ICON_BTN)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("關閉")
        close_btn.clicked.connect(self.reject)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        root.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content.setObjectName("settingsScrollContent")
        layout = QVBoxLayout(content)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 6, 0)

        layout.addWidget(self._section_label("藥水與門檻"))
        keys_group = QGroupBox("藥水按鍵")
        keys_form = QFormLayout(keys_group)
        keys_form.setSpacing(12)
        self.heal_key_btn = KeyCaptureButton()
        self.heal_key_btn.set_key(str(config.get("heal_key", "1")))
        self.mana_key_btn = KeyCaptureButton()
        self.mana_key_btn.set_key(str(config.get("mana_key", "2")))
        keys_form.addRow(self._form_label("補血鍵"), self.heal_key_btn)
        keys_form.addRow(self._form_label("補魔鍵"), self.mana_key_btn)
        layout.addWidget(keys_group)

        threshold_group = QGroupBox("觸發門檻")
        th_layout = QVBoxLayout(threshold_group)
        th_layout.setSpacing(14)
        self.heal_slider, self.heal_label = self._make_slider(
            int(config.get("heal_threshold", 45)), "補血", "life"
        )
        self.mana_slider, self.mana_label = self._make_slider(
            int(config.get("mana_threshold", 45)), "補魔", "mana"
        )
        th_layout.addWidget(self.heal_label)
        th_layout.addWidget(self.heal_slider)
        th_layout.addWidget(self.mana_label)
        th_layout.addWidget(self.mana_slider)
        layout.addWidget(threshold_group)

        layout.addWidget(self._section_label("進階"))
        misc_group = QGroupBox("偵測與冷卻")
        misc_form = QFormLayout(misc_group)
        misc_form.setSpacing(12)
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
        layout.addWidget(misc_group)

        layout.addWidget(self._section_label("熱鍵"))
        hotkey_group = QGroupBox("全域熱鍵")
        hotkey_form = QFormLayout(hotkey_group)
        hotkey_form.setSpacing(12)
        self.hotkey_heal_btn = KeyCaptureButton()
        self.hotkey_heal_btn.set_key(str(config.get("hotkey_heal_toggle", "f6")))
        self.hotkey_mana_btn = KeyCaptureButton()
        self.hotkey_mana_btn.set_key(str(config.get("hotkey_mana_toggle", "f7")))
        self.hotkey_master_btn = KeyCaptureButton()
        self.hotkey_master_btn.set_key(str(config.get("hotkey_master_toggle", "f8")))
        hotkey_form.addRow(self._form_label("補血開關"), self.hotkey_heal_btn)
        hotkey_form.addRow(self._form_label("補魔開關"), self.hotkey_mana_btn)
        hotkey_form.addRow(self._form_label("全域暫停"), self.hotkey_master_btn)
        layout.addWidget(hotkey_group)

        layout.addWidget(self._section_label("球體"))
        cal_group = QGroupBox("校正")
        cal_form = QVBoxLayout(cal_group)
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
        layout.addWidget(cal_group)

        layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll, stretch=1)

        btn_row = QHBoxLayout()
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

        self._attach_drag_handlers(panel)

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

    def _form_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("formLabel")
        return lbl

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setObjectName("sectionTitle")
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
