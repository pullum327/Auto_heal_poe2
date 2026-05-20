"""主浮層 UI — 玻璃擬態風格。"""

from __future__ import annotations

from typing import Any, Literal

from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QMenu,
    QFrame,
    QSizePolicy,
)

from ui.styles import GLASS_MENU

# 玻璃面板
GLASS_PANEL = """
QFrame#glassPanel {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(72, 52, 120, 0.55),
        stop:1 rgba(28, 18, 52, 0.72)
    );
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 18px;
}
"""

GLASS_CARD = """
QFrame#statCard {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 12px;
}
"""

HP_BAR = """
QProgressBar {
    border: none;
    border-radius: 5px;
    background: rgba(0, 0, 0, 0.35);
    min-height: 8px;
    max-height: 8px;
}
QProgressBar::chunk {
    border-radius: 5px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #e53935, stop:1 #ff8a80
    );
}
"""

MP_BAR = """
QProgressBar {
    border: none;
    border-radius: 5px;
    background: rgba(0, 0, 0, 0.35);
    min-height: 8px;
    max-height: 8px;
}
QProgressBar::chunk {
    border-radius: 5px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #1565c0, stop:1 #82b1ff
    );
}
"""

PILL_OFF = """
QPushButton {
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 8px 18px;
    font-weight: 500;
}
QPushButton:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.22);
}
"""

PILL_HEAL_ON = """
QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(229, 57, 53, 0.85), stop:1 rgba(255, 138, 128, 0.75)
    );
    color: #fff;
    border: 1px solid rgba(255, 200, 190, 0.5);
    border-radius: 14px;
    padding: 8px 18px;
    font-weight: 600;
}
"""

PILL_MANA_ON = """
QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(21, 101, 192, 0.9), stop:1 rgba(130, 177, 255, 0.8)
    );
    color: #fff;
    border: 1px solid rgba(180, 210, 255, 0.5);
    border-radius: 14px;
    padding: 8px 18px;
    font-weight: 600;
}
"""

HEADER_ICON_BTN = """
QPushButton#headerIconBtn,
QPushButton#headerCloseBtn {
    background: rgba(255, 255, 255, 0.08);
    color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 10px;
    padding: 0;
    margin: 0;
    font-size: 15px;
    font-family: "Segoe UI";
    font-weight: normal;
}
QPushButton#headerIconBtn:hover {
    background: rgba(255, 255, 255, 0.15);
}
QPushButton#headerCloseBtn:hover {
    background: rgba(229, 57, 53, 0.55);
    color: #fff;
    border-color: rgba(255, 138, 128, 0.6);
}
"""

_HEADER_BTN_SIZE = 30


def _make_header_icon_button(
    text: str,
    tooltip: str,
    *,
    is_close: bool = False,
) -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("headerCloseBtn" if is_close else "headerIconBtn")
    btn.setFixedSize(_HEADER_BTN_SIZE, _HEADER_BTN_SIZE)
    btn.setStyleSheet(HEADER_ICON_BTN)
    btn.setToolTip(tooltip)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn


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
            self.setText(f"{self._label} · ON")
        else:
            self.setText(f"{self._label} · OFF")
            style = PILL_OFF
        self.setStyleSheet(style)


class OverlayWindow(QWidget):
    request_settings = pyqtSignal()
    request_calibrate_life = pyqtSignal()
    request_calibrate_mana = pyqtSignal()
    request_quit = pyqtSignal()
    config_changed = pyqtSignal(dict)

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__()
        self._config = dict(config)
        self._drag_pos: QPoint | None = None
        self._pause_message = ""

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFont(QFont("Segoe UI", 9))

        ox = int(config.get("overlay_x", 100))
        oy = int(config.get("overlay_y", 100))
        self.setGeometry(ox, oy, 300, 248)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        panel = QFrame()
        panel.setObjectName("glassPanel")
        panel.setStyleSheet(GLASS_PANEL + GLASS_CARD)
        outer.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # 標題列
        header = QHBoxLayout()
        title = QLabel("POE2")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #f5f2ff; letter-spacing: 1px;")
        subtitle = QLabel("Auto Flask")
        subtitle.setStyleSheet("color: rgba(200, 190, 255, 0.65); font-size: 9pt;")
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        settings_btn = _make_header_icon_button("⚙", "設定")
        settings_btn.clicked.connect(self.request_settings.emit)

        close_btn = _make_header_icon_button("✕", "關閉程式", is_close=True)
        close_btn.clicked.connect(self.request_quit.emit)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        header.setSpacing(6)
        layout.addLayout(header)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            "color: #ffcc80; font-size: 8pt; padding: 0 4px;"
        )
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # 生命卡片
        layout.addWidget(self._build_stat_card("life", "生命", HP_BAR))
        # 魔力卡片
        layout.addWidget(self._build_stat_card("mana", "魔力", MP_BAR))

        # 開關列（僅補血 / 補魔）
        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(10)
        self.heal_btn = PillToggle("補血", "heal", bool(config.get("heal_enabled", True)))
        self.mana_btn = PillToggle("補魔", "mana", bool(config.get("mana_enabled", True)))
        toggle_row.addWidget(self.heal_btn)
        toggle_row.addWidget(self.mana_btn)
        layout.addLayout(toggle_row)

        self.heal_btn.toggled_state.connect(self._on_heal_toggle)
        self.mana_btn.toggled_state.connect(self._on_mana_toggle)

        hint = QLabel("右鍵選單 · F6/F7 切換 · F8 暫停")
        hint.setStyleSheet("color: rgba(255,255,255,0.35); font-size: 7pt;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)
        self._sync_master_state()

    def _build_stat_card(self, kind: str, name: str, bar_style: str) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(GLASS_CARD)

        row = QHBoxLayout(card)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(10)

        dot_color = "#ff6b6b" if kind == "life" else "#64b5f6"
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {dot_color}; font-size: 10pt;")
        dot.setFixedWidth(16)

        col = QVBoxLayout()
        col.setSpacing(4)

        header = QHBoxLayout()
        label = QLabel(name)
        label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 9pt;")
        pct = QLabel("—")
        pct.setStyleSheet("color: #fff; font-weight: 600; font-size: 11pt;")
        pct.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(label)
        header.addStretch()
        header.addWidget(pct)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        bar.setStyleSheet(bar_style)
        bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        col.addLayout(header)
        col.addWidget(bar)

        row.addWidget(dot)
        row.addLayout(col, stretch=1)

        if kind == "life":
            self.hp_label = pct
            self.hp_bar = bar
        else:
            self.mp_label = pct
            self.mp_bar = bar

        return card

    def get_config(self) -> dict[str, Any]:
        return self._config

    def apply_config(self, config: dict[str, Any]) -> None:
        self._config = dict(config)
        self.heal_btn.set_active(bool(config.get("heal_enabled", True)))
        self.mana_btn.set_active(bool(config.get("mana_enabled", True)))
        self._sync_master_state()

    def update_status(
        self,
        hp: float,
        mp: float,
        anomaly: bool,
        message: str,
    ) -> None:
        if hp < 0:
            self.hp_label.setText("—")
            self.hp_bar.setValue(0)
        else:
            self.hp_label.setText(f"{hp:.0f}%")
            self.hp_bar.setValue(int(max(0, min(100, hp))))

        if mp < 0:
            self.mp_label.setText("—")
            self.mp_bar.setValue(0)
        else:
            self.mp_label.setText(f"{mp:.0f}%")
            self.mp_bar.setValue(int(max(0, min(100, mp))))

        if self._pause_message:
            self.status_label.setText(self._pause_message)
        elif message:
            self.status_label.setText(message)
        elif anomaly:
            self.status_label.setText("偵測異常 — 已暫停按鍵")
        else:
            self.status_label.setText("")

    def toggle_master(self) -> None:
        """F8：全域暫停 / 恢復（無 UI 按鈕）。"""
        enabled = not bool(self._config.get("master_enabled", True))
        self._config["master_enabled"] = enabled
        self._sync_master_state()
        self.status_label.setText(self._pause_message)
        self.config_changed.emit(self._config)

    def toggle_heal(self) -> None:
        self.heal_btn.set_active(not self.heal_btn.is_active())
        self._on_heal_toggle(self.heal_btn.is_active())

    def toggle_mana(self) -> None:
        self.mana_btn.set_active(not self.mana_btn.is_active())
        self._on_mana_toggle(self.mana_btn.is_active())

    def _sync_master_state(self) -> None:
        if self._config.get("master_enabled", True):
            self._pause_message = ""
        else:
            self._pause_message = "⏸ 全域暫停中 · 按 F8 恢復"

    def _on_heal_toggle(self, active: bool) -> None:
        self._config["heal_enabled"] = active
        if active:
            self._config["master_enabled"] = True
            self._sync_master_state()
        self.config_changed.emit(self._config)

    def _on_mana_toggle(self, active: bool) -> None:
        self._config["mana_enabled"] = active
        if active:
            self._config["master_enabled"] = True
            self._sync_master_state()
        self.config_changed.emit(self._config)

    def _show_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(GLASS_MENU)
        menu.addAction("設定", self.request_settings.emit)
        menu.addAction("校正生命球", self.request_calibrate_life.emit)
        menu.addAction("校正魔力球", self.request_calibrate_mana.emit)
        menu.addSeparator()
        menu.addAction("退出", self.request_quit.emit)
        menu.exec(self.mapToGlobal(pos))

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
        if event.button() == Qt.MouseButton.LeftButton:
            self._config["overlay_x"] = self.x()
            self._config["overlay_y"] = self.y()
            self.config_changed.emit(self._config)

    def closeEvent(self, event) -> None:
        self._config["overlay_x"] = self.x()
        self._config["overlay_y"] = self.y()
        super().closeEvent(event)
