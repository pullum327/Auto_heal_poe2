"""共用玻璃擬態 (Glassmorphism) 樣式。"""

GLASS_DIALOG = """
QDialog {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a1035, stop:0.5 #151028, stop:1 #0d0a1f
    );
    color: #ece8ff;
}
QLabel { color: rgba(236, 232, 255, 0.88); }
QGroupBox {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 14px;
    margin-top: 14px;
    padding: 18px 12px 12px 12px;
    font-weight: 600;
    color: #f0ecff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: rgba(255, 255, 255, 0.75);
}
QPushButton {
    background: rgba(255, 255, 255, 0.1);
    color: #f5f2ff;
    border: 1px solid rgba(255, 255, 255, 0.22);
    padding: 9px 16px;
    border-radius: 10px;
    font-weight: 500;
}
QPushButton:hover {
    background: rgba(255, 255, 255, 0.16);
    border-color: rgba(255, 255, 255, 0.35);
}
QPushButton#primaryBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a29bfe
    );
    border: 1px solid rgba(255, 255, 255, 0.3);
}
QPushButton#primaryBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7d6ff0, stop:1 #b3adff
    );
}
QLineEdit, QDoubleSpinBox {
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 7px 10px;
    color: #f0ecff;
}
QSlider::groove:horizontal {
    height: 6px;
    background: rgba(0, 0, 0, 0.35);
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 16px;
    margin: -5px 0;
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #a29bfe, stop:1 #6c5ce7
    );
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 8px;
}
"""

GLASS_MENU = """
QMenu {
    background: rgba(26, 16, 53, 0.95);
    color: #ece8ff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 6px;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: rgba(108, 92, 231, 0.45);
}
"""
