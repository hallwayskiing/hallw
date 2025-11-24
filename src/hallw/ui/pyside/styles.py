# --- Modern Premium Dark Theme ---
STYLE = """
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
    border-radius: 28px;
    padding: 16px 28px;
    color: #ffffff;
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
QPushButton {
    background-color: #4a7fc9;
    color: #ffffff;
    border: none;
    border-radius: 28px;
    padding: 16px 32px;
    font-weight: bold;
    font-size: 16px;
}
QPushButton:hover {
    background-color: #5a8fd9;
}
QPushButton:pressed {
    background-color: #3a6fb9;
}
QPushButton:disabled {
    background-color: #1a1a1a;
    color: #4a4a4a;
}

/* Toggle Sidebar Button (Close) & Show Sidebar Button (Restore) */
QPushButton#HideSidebar, QPushButton#ShowSidebar {
    background-color: #1a1a1a;
    color: #888888;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 0px;
    font-size: 26px;
    font-weight: normal;
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
