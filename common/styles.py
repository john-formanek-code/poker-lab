DARK_THEME = """
QMainWindow, QDialog, QWidget {
    background-color: #000000;
    color: #dcdcdc;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
}

/* Sidebar / Navigation */
QListWidget#sidebar {
    background-color: #050505;
    border-right: 1px solid #1a1a1a;
    color: #888888;
    outline: none;
}

QListWidget#sidebar::item {
    padding: 20px;
    border-bottom: 1px solid #0a0a0a;
}

QListWidget#sidebar::item:selected {
    background-color: #111111;
    color: #ffffff;
    border-left: 3px solid #ffffff;
}

/* Buttons - Sharp and Minimal */
QPushButton {
    background-color: #0a0a0a;
    color: #ffffff;
    border: 1px solid #222222;
    border-radius: 0px;
    padding: 10px 20px;
    text-transform: uppercase;
    font-weight: bold;
    letter-spacing: 1px;
}

QPushButton:hover {
    background-color: #151515;
    border-color: #444444;
}

QPushButton:pressed {
    background-color: #ffffff;
    color: #000000;
}

QPushButton:disabled {
    color: #333333;
    border-color: #111111;
}

QPushButton#action_btn {
    border: 1px solid #ffffff;
}

/* Inputs */
QComboBox, QSpinBox, QLineEdit {
    background-color: #0a0a0a;
    border: 1px solid #222222;
    border-radius: 0px;
    padding: 6px;
    color: #ffffff;
}

QComboBox::drop-down {
    border: none;
}

QSlider::groove:horizontal {
    border: 1px solid #222222;
    height: 4px;
    background: #0a0a0a;
}

QSlider::handle:horizontal {
    background: #ffffff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
}

/* Specific Game Elements */
QFrame#table_container {
    background-color: #030303;
    border: 1px solid #1a1a1a;
    border-radius: 0px;
}

QLabel#card {
    background-color: #ffffff;
    color: #000000;
    border-radius: 2px;
    font-size: 20px;
    font-weight: 900;
    min-width: 45px;
    min-height: 65px;
}

QLabel#status_bar {
    background-color: #080808;
    color: #666666;
    border-top: 1px solid #1a1a1a;
    padding: 8px 15px;
    font-size: 11px;
    text-transform: uppercase;
}

QGroupBox {
    border: 1px solid #1a1a1a;
    margin-top: 20px;
    font-weight: bold;
    text-transform: uppercase;
    color: #555555;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QScrollArea {
    border: none;
}

QSplitter::handle {
    background-color: #111111;
}
"""
