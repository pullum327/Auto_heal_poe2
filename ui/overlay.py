"""主浮層 UI — 玻璃擬態風格。"""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt, QPoint, pyqtSignal
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

from ui.styles import (
    GLASS_MENU,
    GLASS_PANEL,
    GLASS_CARD,
    GLASS_DIVIDER,
    HP_BAR,
    MP_BAR,
    HEADER_ICON_BTN,
)
from ui.widgets import PillToggle, StatusDot, ui_font

_HEADER_BTN_SIZE = 32


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
        self._heal_threshold = float(config.get("heal_threshold", 45))
        self._mana_threshold = float(config.get("mana_threshold", 45))

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFont(ui_font(9))

        ox = int(config.get("overlay_x", 100))
        oy = int(config.get("overlay_y", 100))
        self.setGeometry(ox, oy, 312, 252)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        panel = QFrame()
        panel.setObjectName("glassPanel")
        panel.setStyleSheet(GLASS_PANEL)
        outer.addWidget(panel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("POE2")
        title.setFont(ui_font(14, bold=True))
        title.setStyleSheet("color: #faf8ff; letter-spacing: 2px;")
        subtitle = QLabel("Auto Flask")
        subtitle.setStyleSheet("color: rgba(190, 180, 255, 0.7); font-size: 8pt;")

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        self._status_dot = StatusDot()

        settings_btn = _make_header_icon_button("⚙", "設定")
        settings_btn.clicked.connect(self.request_settings.emit)
        close_btn = _make_header_icon_button("✕", "關閉程式", is_close=True)
        close_btn.clicked.connect(self.request_quit.emit)

        header.addLayout(title_box)
        header.addStretch()
        header.addWidget(self._status_dot, alignment=Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        header.setSpacing(8)
        layout.addLayout(header)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setStyleSheet(GLASS_DIVIDER)
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        layout.addWidget(self._build_stat_card("life", "生命", HP_BAR))
        layout.addWidget(self._build_stat_card("mana", "魔力", MP_BAR))

        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(12)
        self.heal_btn = PillToggle("補血", "heal", bool(config.get("heal_enabled", True)))
        self.mana_btn = PillToggle("補魔", "mana", bool(config.get("mana_enabled", True)))
        toggle_row.addWidget(self.heal_btn, stretch=1)
        toggle_row.addWidget(self.mana_btn, stretch=1)
        layout.addLayout(toggle_row)

        self.heal_btn.toggled_state.connect(self._on_heal_toggle)
        self.mana_btn.toggled_state.connect(self._on_mana_toggle)

        hint = QLabel("拖曳移動 · 右鍵選單 · F6/F7 開關 · F8 暫停")
        hint.setStyleSheet("color: rgba(255,255,255,0.32); font-size: 7pt;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)
        self._sync_master_state()
        self._refresh_status_dot()

    def _build_stat_card(self, kind: str, name: str, bar_style: str) -> QFrame:
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(GLASS_CARD)

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(12)

        accent = "#ef5350" if kind == "life" else "#42a5f5"
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {accent}; font-size: 11pt;")
        dot.setFixedWidth(18)

        col = QVBoxLayout()
        col.setSpacing(6)

        header = QHBoxLayout()
        label = QLabel(name)
        label.setStyleSheet("color: rgba(255,255,255,0.65); font-size: 9pt;")
        pct = QLabel("—")
        pct.setStyleSheet("color: #fff; font-weight: 700; font-size: 13pt;")
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
        self._heal_threshold = float(config.get("heal_threshold", 45))
        self._mana_threshold = float(config.get("mana_threshold", 45))
        self.heal_btn.set_active(bool(config.get("heal_enabled", True)))
        self.mana_btn.set_active(bool(config.get("mana_enabled", True)))
        self._sync_master_state()
        self._refresh_status_dot()

    def _pct_style(self, value: float, threshold: float, accent: str) -> str:
        if value < 0:
            return "color: rgba(255,255,255,0.35); font-weight: 700; font-size: 13pt;"
        if value < threshold:
            return (
                "color: #ffab91; font-weight: 700; font-size: 13pt;"
            )
        return f"color: {accent}; font-weight: 700; font-size: 13pt;"

    def update_status(
        self,
        hp: float,
        mp: float,
        anomaly: bool,
        message: str,
    ) -> None:
        _ = anomaly, message
        if hp < 0:
            self.hp_label.setText("—")
            self.hp_bar.setValue(0)
            self.hp_label.setStyleSheet(self._pct_style(-1, 0, "#fff"))
        else:
            self.hp_label.setText(f"{hp:.0f}%")
            self.hp_bar.setValue(int(max(0, min(100, hp))))
            self.hp_label.setStyleSheet(
                self._pct_style(hp, self._heal_threshold, "#ff8a80")
            )

        if mp < 0:
            self.mp_label.setText("—")
            self.mp_bar.setValue(0)
            self.mp_label.setStyleSheet(self._pct_style(-1, 0, "#fff"))
        else:
            self.mp_label.setText(f"{mp:.0f}%")
            self.mp_bar.setValue(int(max(0, min(100, mp))))
            self.mp_label.setStyleSheet(
                self._pct_style(mp, self._mana_threshold, "#82b1ff")
            )

        self._refresh_status_dot()

    def _refresh_status_dot(self) -> None:
        if self._config.get("master_enabled", True):
            self._status_dot.set_running()
        else:
            self._status_dot.set_paused()

    def toggle_master(self) -> None:
        enabled = not bool(self._config.get("master_enabled", True))
        self._config["master_enabled"] = enabled
        self._sync_master_state()
        self._refresh_status_dot()
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
        self.config_changed.emit(self._config)

    def _on_mana_toggle(self, active: bool) -> None:
        self._config["mana_enabled"] = active
        self.config_changed.emit(self._config)

    def _show_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(GLASS_MENU)
        menu.addAction("⚙  設定", self.request_settings.emit)
        menu.addSeparator()
        menu.addAction("◎  校正生命球", self.request_calibrate_life.emit)
        menu.addAction("◎  校正魔力球", self.request_calibrate_mana.emit)
        menu.addSeparator()
        menu.addAction("✕  退出", self.request_quit.emit)
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
