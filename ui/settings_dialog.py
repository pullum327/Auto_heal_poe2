"""設定對話框。"""

from __future__ import annotations

from typing import Any, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QWidget,
)

from ui.styles import GLASS_DIALOG as STYLESHEET


class KeyCaptureButton(QPushButton):
    def __init__(self, label: str = "點擊錄製") -> None:
        super().__init__(label)
        self._capturing = False
        self._key = ""
        self.clicked.connect(self._start_capture)

    def key(self) -> str:
        return self._key

    def set_key(self, key: str) -> None:
        self._key = key
        self.setText(key.upper() if key else "點擊錄製")

    def _start_capture(self) -> None:
        self._capturing = True
        self.setText("請按下按鍵…")
        self.setFocus()

    def keyPressEvent(self, event) -> None:
        if not self._capturing:
            super().keyPressEvent(event)
            return
        key = event.key()
        text = event.text()
        if key == Qt.Key.Key_Escape:
            self._capturing = False
            self.setText(self._key.upper() if self._key else "點擊錄製")
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
        self._capturing = False
        self.setText(self._key.upper() if self._key else "點擊錄製")


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

        self.setWindowTitle("POE2 自動補瓶 — 設定")
        self.setMinimumWidth(420)
        self.setStyleSheet(STYLESHEET)
        self.setFont(QFont("Microsoft JhengHei", 10))

        layout = QVBoxLayout(self)

        keys_group = QGroupBox("藥水按鍵")
        keys_form = QFormLayout(keys_group)
        self.heal_key_btn = KeyCaptureButton()
        self.heal_key_btn.set_key(str(config.get("heal_key", "1")))
        self.mana_key_btn = KeyCaptureButton()
        self.mana_key_btn.set_key(str(config.get("mana_key", "2")))
        keys_form.addRow("補血鍵", self.heal_key_btn)
        keys_form.addRow("補魔鍵", self.mana_key_btn)
        layout.addWidget(keys_group)

        threshold_group = QGroupBox("觸發門檻 (%)")
        th_layout = QVBoxLayout(threshold_group)
        self.heal_slider, self.heal_label = self._make_slider(
            int(config.get("heal_threshold", 45)), "補血門檻"
        )
        self.mana_slider, self.mana_label = self._make_slider(
            int(config.get("mana_threshold", 45)), "補魔門檻"
        )
        th_layout.addWidget(self.heal_label)
        th_layout.addWidget(self.heal_slider)
        th_layout.addWidget(self.mana_label)
        th_layout.addWidget(self.mana_slider)
        layout.addWidget(threshold_group)

        misc_group = QGroupBox("其他")
        misc_form = QFormLayout(misc_group)
        self.cooldown_spin = QDoubleSpinBox()
        self.cooldown_spin.setRange(0.5, 3.0)
        self.cooldown_spin.setSingleStep(0.1)
        self.cooldown_spin.setValue(float(config.get("potion_cooldown", 1.0)))
        misc_form.addRow("藥水冷卻 (秒)", self.cooldown_spin)

        self.hotkey_heal = QLineEdit(str(config.get("hotkey_heal_toggle", "f6")))
        self.hotkey_mana = QLineEdit(str(config.get("hotkey_mana_toggle", "f7")))
        self.hotkey_master = QLineEdit(str(config.get("hotkey_master_toggle", "f8")))
        misc_form.addRow("熱鍵：補血開關", self.hotkey_heal)
        misc_form.addRow("熱鍵：補魔開關", self.hotkey_mana)
        misc_form.addRow("熱鍵：全域暫停 (F8)", self.hotkey_master)
        layout.addWidget(misc_group)

        cal_group = QGroupBox("球體校正（點擊球心）")
        cal_form = QVBoxLayout(cal_group)
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(5.0, 12.0)
        self.radius_spin.setSingleStep(0.5)
        self.radius_spin.setSuffix(" %")
        self.radius_spin.setValue(float(config.get("orb_radius_percent", 7.5)))
        radius_row = QHBoxLayout()
        radius_row.addWidget(QLabel("球體半徑（螢幕高度 %）"))
        radius_row.addWidget(self.radius_spin)
        cal_form.addLayout(radius_row)

        cal_layout = QHBoxLayout()
        btn_life = QPushButton("校正生命球")
        btn_mana = QPushButton("校正魔力球")
        btn_life.clicked.connect(self._calibrate_life)
        btn_mana.clicked.connect(self._calibrate_mana)
        cal_layout.addWidget(btn_life)
        cal_layout.addWidget(btn_mana)
        cal_form.addLayout(cal_layout)
        layout.addWidget(cal_group)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("儲存")
        save_btn.setObjectName("primaryBtn")
        cancel_btn = QPushButton("取消")
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _make_slider(self, value: int, prefix: str) -> tuple[QSlider, QLabel]:
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(10, 90)
        slider.setValue(value)
        label = QLabel(f"{prefix}: {value}%")
        slider.valueChanged.connect(lambda v: label.setText(f"{prefix}: {v}%"))
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
        self._config["orb_radius_percent"] = self.radius_spin.value()
        self._config["hotkey_heal_toggle"] = self.hotkey_heal.text().strip().lower() or "f6"
        self._config["hotkey_mana_toggle"] = self.hotkey_mana.text().strip().lower() or "f7"
        self._config["hotkey_master_toggle"] = (
            self.hotkey_master.text().strip().lower() or "f8"
        )
        self._on_save(self._config)
        self.accept()
