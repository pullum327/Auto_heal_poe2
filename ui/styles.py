"""共用 UI 樣式與字型。"""

FONT_FAMILY = "Microsoft JhengHei, Segoe UI"

GLASS_DIALOG_SHELL = """
QDialog {
    background: transparent;
}
"""

GLASS_DIALOG_PANEL = """
QFrame#glassDialogPanel {
    background-color: #322454;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #3d2d5c,
        stop:0.45 #2a1e42,
        stop:1 #181024
    );
    border: 1px solid rgba(190, 180, 255, 0.5);
    border-radius: 20px;
}
"""

GLASS_DIALOG_CONTENT = f"""
QFrame#glassDialogPanel QLabel {{
    color: #ebe9f7;
    font-family: {FONT_FAMILY};
}}
QLabel#dialogTitle {{
    color: #ffffff;
    font-weight: bold;
}}
QLabel#sectionTitle {{
    color: rgba(186, 176, 255, 0.92);
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 10px 2px 4px 2px;
}}
QLabel#formLabel {{
    color: rgba(235, 232, 255, 0.88);
    font-size: 10pt;
    min-width: 72px;
}}
QLabel#thresholdLife {{
    color: #ff9e94;
    font-weight: 700;
    font-size: 10pt;
}}
QLabel#thresholdMana {{
    color: #90caf9;
    font-weight: 700;
    font-size: 10pt;
}}
QScrollArea {{
    background-color: #2a1e42;
    border: none;
}}
QScrollArea > QWidget > QWidget,
QWidget#settingsScrollContent {{
    background-color: #2a1e42;
}}
QGroupBox {{
    background-color: #1f1632;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 14px;
    margin-top: 18px;
    padding: 22px 14px 14px 14px;
    font-weight: 600;
    color: #f0ecff;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 10px;
    color: #e0dbff;
}}
QPushButton {{
    background: rgba(255, 255, 255, 0.08);
    color: #f5f2ff;
    border: 1px solid rgba(255, 255, 255, 0.18);
    padding: 10px 18px;
    border-radius: 10px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background: rgba(255, 255, 255, 0.14);
    border-color: rgba(255, 255, 255, 0.32);
}}
QPushButton#primaryBtn {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #9b8cff
    );
    border: 1px solid rgba(255, 255, 255, 0.28);
    font-weight: 600;
}}
QPushButton#primaryBtn:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7d6ff0, stop:1 #b3adff
    );
}}
QPushButton#calLifeBtn {{
    background: rgba(229, 57, 53, 0.25);
    border-color: rgba(255, 138, 128, 0.45);
}}
QPushButton#calLifeBtn:hover {{
    background: rgba(229, 57, 53, 0.4);
}}
QPushButton#calManaBtn {{
    background: rgba(21, 101, 192, 0.3);
    border-color: rgba(130, 177, 255, 0.45);
}}
QPushButton#calManaBtn:hover {{
    background: rgba(21, 101, 192, 0.45);
}}
QPushButton#keyCaptureBtn {{
    background: rgba(0, 0, 0, 0.45);
    color: #ffffff;
    border: 1px dashed rgba(162, 155, 254, 0.65);
    min-width: 88px;
    font-weight: 600;
    letter-spacing: 1px;
}}
QPushButton#keyCaptureBtn[capturing="true"] {{
    border-style: solid;
    border-color: #a29bfe;
    background: rgba(108, 92, 231, 0.35);
    color: #fff;
}}
QLineEdit, QDoubleSpinBox, QSpinBox {{
    background: rgba(0, 0, 0, 0.42);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 8px;
    padding: 8px 10px;
    color: #f0ecff;
    min-height: 18px;
}}
QSlider::groove:horizontal {{
    height: 8px;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 4px;
}}
QSlider::sub-page:horizontal {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a29bfe
    );
    border-radius: 4px;
}}
QSlider::handle:horizontal {{
    width: 18px;
    margin: -6px 0;
    background: #ece8ff;
    border: 2px solid #6c5ce7;
    border-radius: 9px;
}}
QScrollBar:vertical {{
    width: 8px;
    background: transparent;
}}
QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    min-height: 24px;
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
