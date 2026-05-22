"""共用 UI 樣式與字型。"""

FONT_FAMILY = "Microsoft JhengHei, Segoe UI"

GLASS_DIALOG_SHELL = """
QDialog {
    background: transparent;
}
"""

# 設定頁面板自繪漸層色（淺色不透明，避免穿透遊戲畫面）
SETTINGS_PANEL_RADIUS = 22
SETTINGS_GRADIENT_TOP = (148, 142, 178)
SETTINGS_GRADIENT_MID = (132, 126, 162)
SETTINGS_GRADIENT_BOTTOM = (116, 110, 148)
SETTINGS_BORDER_OUTER = (255, 255, 255, 140)
SETTINGS_BORDER_INNER = (255, 255, 255, 55)
SETTINGS_HIGHLIGHT_TOP = (255, 255, 255, 48)

GLASS_DIALOG_PANEL = """
QFrame#glassDialogPanel {
    background: transparent;
    border: none;
}
"""

GLASS_DIALOG_CONTENT = f"""
QFrame#glassDialogPanel QLabel {{
    color: #3a3550;
    font-family: {FONT_FAMILY};
}}
QLabel#dialogTitle {{
    color: #2a2640;
    font-weight: bold;
}}
QLabel#formLabel {{
    color: #5c5678;
    font-size: 10pt;
    min-width: 72px;
}}
QLabel#thresholdLife {{
    color: #c45c52;
    font-weight: 700;
    font-size: 10pt;
}}
QLabel#thresholdMana {{
    color: #4a7ab8;
    font-weight: 700;
    font-size: 10pt;
}}
QFrame#settingsHeaderDivider {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(255, 255, 255, 0),
        stop:0.5 rgba(255, 255, 255, 0.55),
        stop:1 rgba(255, 255, 255, 0)
    );
    max-height: 1px;
    min-height: 1px;
    border: none;
}}
QScrollArea#settingsScroll {{
    background-color: #b4aed0;
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-radius: 14px;
}}
QScrollArea#settingsScroll > QWidget > QWidget {{
    background-color: #b4aed0;
    border-radius: 14px;
}}
QWidget#settingsScrollContent {{
    background-color: #b4aed0;
}}
QFrame#settingsSection {{
    background-color: #c8c2dc;
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: 16px;
}}
QPushButton {{
    background-color: rgba(255, 255, 255, 0.42);
    color: #3a3550;
    border: 1px solid rgba(255, 255, 255, 0.65);
    padding: 10px 18px;
    border-radius: 12px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.62);
    border-color: rgba(255, 255, 255, 0.85);
}}
QPushButton#primaryBtn {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #8b7ec8, stop:1 #b8b0e8
    );
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.55);
    font-weight: 600;
}}
QPushButton#primaryBtn:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #9d90d4, stop:1 #ccc6f0
    );
}}
QPushButton#calLifeBtn {{
    background-color: rgba(255, 220, 215, 0.75);
    color: #8b3a34;
    border-color: rgba(220, 120, 110, 0.45);
}}
QPushButton#calLifeBtn:hover {{
    background-color: rgba(255, 200, 195, 0.9);
}}
QPushButton#calManaBtn {{
    background-color: rgba(210, 228, 255, 0.8);
    color: #2e5a8a;
    border-color: rgba(120, 160, 220, 0.45);
}}
QPushButton#calManaBtn:hover {{
    background-color: rgba(195, 218, 255, 0.95);
}}
QPushButton#keyCaptureBtn {{
    background-color: rgba(255, 255, 255, 0.5);
    color: #3a3550;
    border: 1px dashed rgba(120, 108, 168, 0.55);
    min-width: 88px;
    font-weight: 600;
    letter-spacing: 1px;
}}
QPushButton#keyCaptureBtn[capturing="true"] {{
    border-style: solid;
    border-color: #8b7ec8;
    background-color: rgba(200, 190, 235, 0.85);
    color: #2a2640;
}}
QLineEdit, QDoubleSpinBox, QSpinBox {{
    background-color: rgba(255, 255, 255, 0.48);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 10px;
    padding: 8px 10px;
    color: #3a3550;
    min-height: 18px;
}}
QSlider::groove:horizontal {{
    height: 6px;
    background: rgba(255, 255, 255, 0.45);
    border-radius: 3px;
}}
QSlider::sub-page:horizontal {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #9d90d4, stop:1 #c4b8e8
    );
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    width: 16px;
    margin: -5px 0;
    background: #ffffff;
    border: 2px solid #9d90d4;
    border-radius: 8px;
}}
QScrollBar:vertical {{
    width: 6px;
    background: transparent;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: rgba(90, 82, 130, 0.28);
    border-radius: 3px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(90, 82, 130, 0.42);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""

GLASS_MENU = """
QMenu {
    background: rgba(22, 14, 44, 0.96);
    color: #ece8ff;
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 12px;
    padding: 8px 4px;
    font-size: 10pt;
}
QMenu::item {
    padding: 10px 28px;
    border-radius: 8px;
    margin: 2px 6px;
}
QMenu::item:selected {
    background: rgba(108, 92, 231, 0.5);
}
QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.12);
    margin: 6px 12px;
}
"""

GLASS_PANEL = """
QFrame#glassPanel {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(58, 42, 98, 0.62),
        stop:0.5 rgba(36, 24, 68, 0.78),
        stop:1 rgba(18, 12, 38, 0.88)
    );
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
}
"""

GLASS_CARD = """
QFrame#statCard {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
}
"""

GLASS_DIVIDER = """
QFrame#divider {
    background: rgba(255, 255, 255, 0.1);
    max-height: 1px;
    min-height: 1px;
    border: none;
}
"""

def glass_dialog_stylesheet() -> str:
    return GLASS_DIALOG_SHELL

def glass_dialog_panel_stylesheet() -> str:
    return GLASS_DIALOG_PANEL + GLASS_DIALOG_CONTENT

HP_BAR = """
QProgressBar {
    border: none;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.4);
    min-height: 10px;
    max-height: 10px;
}
QProgressBar::chunk {
    border-radius: 6px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #c62828, stop:1 #ff8a80
    );
}
"""

MP_BAR = """
QProgressBar {
    border: none;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.4);
    min-height: 10px;
    max-height: 10px;
}
QProgressBar::chunk {
    border-radius: 6px;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #0d47a1, stop:1 #82b1ff
    );
}
"""

PILL_OFF = """
QPushButton {
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 10px 16px;
    font-weight: 500;
    font-size: 9pt;
}
QPushButton:hover {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.65);
}
"""

PILL_HEAL_ON = """
QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(198, 40, 40, 0.9), stop:1 rgba(255, 138, 128, 0.75)
    );
    color: #fff;
    border: 1px solid rgba(255, 200, 190, 0.55);
    border-radius: 16px;
    padding: 10px 16px;
    font-weight: 600;
    font-size: 9pt;
}
"""

PILL_MANA_ON = """
QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(13, 71, 161, 0.92), stop:1 rgba(100, 181, 246, 0.82)
    );
    color: #fff;
    border: 1px solid rgba(180, 210, 255, 0.55);
    border-radius: 16px;
    padding: 10px 16px;
    font-weight: 600;
    font-size: 9pt;
}
"""

SETTINGS_HEADER_BTN = """
QPushButton#headerCloseBtn {
    background-color: rgba(255, 255, 255, 0.38);
    color: #4a4568;
    border: 1px solid rgba(255, 255, 255, 0.65);
    border-radius: 11px;
    padding: 0;
    margin: 0;
    font-size: 14px;
    font-weight: normal;
}
QPushButton#headerCloseBtn:hover {
    background-color: rgba(235, 120, 115, 0.55);
    color: #5c2020;
    border-color: rgba(220, 140, 135, 0.7);
}
"""

HEADER_ICON_BTN = """
QPushButton#headerIconBtn,
QPushButton#headerCloseBtn {
    background: rgba(255, 255, 255, 0.07);
    color: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 11px;
    padding: 0;
    margin: 0;
    font-size: 14px;
    font-weight: normal;
}
QPushButton#headerIconBtn:hover {
    background: rgba(108, 92, 231, 0.45);
    border-color: rgba(162, 155, 254, 0.6);
}
QPushButton#headerCloseBtn:hover {
    background: rgba(229, 57, 53, 0.55);
    color: #fff;
    border-color: rgba(255, 138, 128, 0.55);
}
"""

CALIB_OVERLAY_BTN = """
QPushButton {
    background: rgba(108, 92, 231, 0.85);
    color: white;
    padding: 10px 22px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.25);
    font-weight: 600;
    min-width: 100px;
}
QPushButton:hover {
    background: rgba(125, 111, 240, 0.95);
}
QPushButton#calCancelBtn {
    background: rgba(255, 255, 255, 0.12);
}
QPushButton#calCancelBtn:hover {
    background: rgba(255, 255, 255, 0.2);
}
"""

CALIB_HINT_LIFE = """
QLabel {
    color: #fff;
    background: rgba(198, 40, 40, 0.35);
    border: 1px solid rgba(255, 138, 128, 0.4);
    padding: 14px 16px;
    border-radius: 12px;
    font-size: 11pt;
}
"""

CALIB_HINT_MANA = """
QLabel {
    color: #fff;
    background: rgba(13, 71, 161, 0.4);
    border: 1px solid rgba(130, 177, 255, 0.45);
    padding: 14px 16px;
    border-radius: 12px;
    font-size: 11pt;
}
"""
