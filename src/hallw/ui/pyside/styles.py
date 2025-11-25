# --- Modern Premium Dark Theme ---
MAIN_STYLE = """
/* Global Background */
QMainWindow {
    background-color: #0a0a0a;
}
QWidget {
    background-color: #0a0a0a;
    color: #e8e8e8;
    font-family: 'Segoe UI', 'Microsoft YaHei UI', 'PingFang SC', 'Noto Sans CJK SC', 'Source Han Sans SC', 'Roboto', sans-serif;
    font-size: 16px;
}

/* Chat Main Window */
QTextEdit {
    background-color: #0a0a0a;
    border: none;
    padding: 8px;
    selection-background-color: #1e3a5f;
    selection-color: #b8d4ff;
}

/* Sidebar */
QTextEdit#Sidebar {
    background-color: #111111;
    border: 1px solid #1f1f1f;
    border-radius: 12px;
    padding: 20px;
    font-family: 'Consolas', 'Sarasa Mono SC', 'Microsoft YaHei Mono', 'Noto Sans Mono CJK SC', 'PingFang SC', 'Courier New', monospace;
    font-size: 14px;
    color: #a8a8a8;
}

/* Input Field */
QLineEdit {
    background-color: #161616;
    border: 1px solid #2a2a2a;
    padding: 0px 24px;
    color: #ffffff;
    max-height: 48px;
    min-height: 48px;
    border-radius: 24px;
    font-size: 16px;
}
QLineEdit:focus {
    border: 2px solid #5e8fd8;
    background-color: #1a1a1a;
}
QLineEdit:disabled {
    background-color: #0f0f0f;
    color: #4a4a4a;
    border: 1px solid #1a1a1a;
}

/* Buttons */
QPushButton#SendButton {
    background-color: #4a7fc9;
    color: #ffffff;
    border: none;
    padding: 0px 24px;
    font-weight: bold;
    max-height: 48px;
    min-height: 48px;
    max-width: 60px;
    min-width: 60px;
    border-radius: 24px;
    font-size: 16px;
}
QPushButton#SendButton:hover {
    background-color: #5a8fd9;
}
QPushButton#SendButton:pressed {
    background-color: #3a6fb9;
}
QPushButton#SendButton:disabled {
    background-color: #1a1a1a;
    color: #4a4a4a;
}

/* Settings Button */
QPushButton#SettingsButton {
    background-color: #4a7fc9;
    color: #ffffff;
    border: none;
    padding: 0px;
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    border-radius: 24px;
    font-size: 20px;
}
QPushButton#SettingsButton:hover {
    background-color: #5a8fd9;
}
QPushButton#SettingsButton:pressed {
    background-color: #3a6fb9;
}

/* Hide/Show Sidebar Button */
QPushButton#HideSidebar, QPushButton#ShowSidebar {
    background-color: #1a1a1a;
    color: #888888;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 0px;
    font-size: 26px;
    font-weight: bold;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
}
QPushButton#HideSidebar:hover, QPushButton#ShowSidebar:hover {
    background-color: #252525;
    color: #aaaaaa;
    border: 1px solid #3a3a3a;
}
QPushButton#HideSidebar:pressed, QPushButton#ShowSidebar:pressed {
    background-color: #151515;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #0a0a0a;
    width: 8px;
    margin: 0px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #2a2a2a;
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #3a3a3a;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
    border: none;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

/* Section Labels */
QLabel {
    background-color: transparent;
    color: #888888;
    font-size: 14px;
    font-weight: bold;
    padding: 8px 4px;
}

/* Splitter */
QSplitter::handle {
    background-color: #1a1a1a;
}
QSplitter::handle:horizontal {
    width: 1px;
}
QSplitter::handle:vertical {
    height: 1px;
}
"""

SETTINGS_STYLE = """
/* Settings Dialog Theme */
QDialog {
    background-color: #121212;
    color: #ffffff;
}
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #1e1e1e;
}
QTabBar::tab {
    background-color: #2d2d2d;
    color: #b0b0b0;
    padding: 8px 16px;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-bottom: 1px solid #1e1e1e;
}
QLabel {
    color: #e0e0e0;
    font-weight: bold;
    background-color: transparent;
    qproperty-alignment: 'AlignVCenter | AlignRight';
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #444444;
    padding: 6px;
    border-radius: 4px;
    min-height: 18px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #4a90e2;
    background-color: #333333;
}

QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
    background: transparent;
    min-height: 40px;
    margin-left: 2px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #555555;
    border-radius: 4px;
    background-color: #2d2d2d;
    subcontrol-position: center left;
}

QCheckBox::indicator:hover {
    border: 1px solid #777777;
    background-color: #383838;
}

QCheckBox::indicator:checked {
    background-color: #4a90e2;
    border: 1px solid #4a90e2;
}

QPushButton {
    background-color: #3a3a3a;
    color: #ffffff;
    border: 1px solid #555555;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #4a4a4a;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QWidget#TabContent {
    background-color: #1e1e1e;
}
"""
