import os
from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QCloseEvent, QIcon, QResizeEvent, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .qt_renderer import QtAgentRenderer
from .settings_dialog import SettingsDialog
from .styles import MAIN_STYLE
from .templates import (
    AI_HEADER_TEMPLATE,
    END_MSG_TEMPLATE,
    ERROR_MSG_TEMPLATE,
    INFO_TEMPLATE,
    USER_MSG_TEMPLATE,
    WELCOME_HTML,
)

# --- Constants ---
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSET_DIR, "logo.ico")

# Responsive breakpoints
BREAKPOINT_SMALL = 1024
BREAKPOINT_MEDIUM = 1366
SIDEBAR_AUTO_SHOW_WIDTH = 900


@dataclass(frozen=True)
class LayoutConfig:
    """Responsive layout configuration."""

    width: int
    height: int
    sidebar_visible: bool
    margins: int
    spacing: int
    chat_padding: int
    sidebar_margin: int
    input_height: int
    button_width: int
    split_ratio: tuple[float, float]

    @classmethod
    def for_screen_width(cls, screen_width: int) -> "LayoutConfig":
        """Factory method to create config based on screen width."""
        if screen_width < BREAKPOINT_SMALL:
            return cls(
                width=min(900, int(screen_width * 0.9)),
                height=700,
                sidebar_visible=False,
                margins=20,
                spacing=16,
                chat_padding=20,
                sidebar_margin=15,
                input_height=52,
                button_width=120,
                split_ratio=(1.0, 0.0),
            )
        if screen_width < BREAKPOINT_MEDIUM:
            return cls(
                width=1100,
                height=750,
                sidebar_visible=True,
                margins=28,
                spacing=20,
                chat_padding=24,
                sidebar_margin=16,
                input_height=56,
                button_width=130,
                split_ratio=(0.72, 0.28),
            )
        return cls(
            width=1200,
            height=800,
            sidebar_visible=True,
            margins=32,
            spacing=24,
            chat_padding=28,
            sidebar_margin=18,
            input_height=60,
            button_width=140,
            split_ratio=(0.74, 0.26),
        )


class QtAgentMainWindow(QMainWindow):
    """Main application window with chat interface and tool sidebar."""

    def __init__(
        self,
        renderer: QtAgentRenderer,
        start_task_callback: Callable[[str], None],
        stop_task_callback: Callable[[], None],
        cleanup_callback: Callable[[], None] | None = None,
    ):
        super().__init__()
        self._renderer = renderer
        self._start_task_callback = start_task_callback
        self._stop_task_callback = stop_task_callback
        self._cleanup_callback = cleanup_callback

        # State flags
        self._is_task_running = False
        self._is_first_interaction = True
        self._sidebar_manually_hidden = False

        # AI streaming state
        self._ai_buffer = ""
        self._ai_start_pos = 0
        self._ai_header_shown = False

        # UI Components (initialized in _setup_ui)
        self._splitter: QSplitter
        self._chat_header: QWidget
        self._agent_output: QTextEdit
        self._tool_plan: QTextEdit
        self._tool_execution: QTextEdit
        self._input_field: QLineEdit
        self._send_btn: QPushButton
        self._settings_btn: QPushButton
        self._sidebar: QWidget
        self._toggle_btns: dict[str, QPushButton] = {}
        self._sidebar_split_ratio: tuple[float, float] = (0.74, 0.26)

        self._init_window()
        self._setup_ui()
        self._connect_signals()
        self._apply_responsive_layout()
        self._show_welcome()

    # --- Initialization ---
    def _init_window(self) -> None:
        self.setWindowTitle("HALLW")
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))
        self.setStyleSheet(MAIN_STYLE)

    def _setup_ui(self) -> None:
        """Setup main UI components and layout."""
        central = QWidget()
        self.setCentralWidget(central)
        self._main_layout = QVBoxLayout(central)

        # Splitter with chat and sidebar
        self._splitter = QSplitter(Qt.Horizontal)
        self._splitter.setHandleWidth(1)
        self._main_layout.addWidget(self._splitter, stretch=1)

        self._setup_chat_area()
        self._setup_sidebar()
        self._setup_input_area()

    def _setup_chat_area(self) -> None:
        """Setup left chat container."""
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Header with show sidebar button
        self._chat_header = QWidget()
        header_layout = QHBoxLayout(self._chat_header)
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.addStretch()
        self._toggle_btns["show"] = self._create_button(
            "◨", "Show Sidebar", self._toggle_sidebar, "ShowSidebar"
        )
        header_layout.addWidget(self._toggle_btns["show"])
        chat_layout.addWidget(self._chat_header)

        self._agent_output = QTextEdit(readOnly=True)
        chat_layout.addWidget(self._agent_output)
        self._splitter.addWidget(chat_container)

    def _setup_sidebar(self) -> None:
        """Setup right sidebar with planning and execution panels."""
        self._sidebar = QWidget()
        layout = QVBoxLayout(self._sidebar)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("📋 PLANNING"))
        header.addStretch()
        self._toggle_btns["hide"] = self._create_button(
            "◧", "Hide Sidebar", self._toggle_sidebar, "HideSidebar"
        )
        header.addWidget(self._toggle_btns["hide"])
        layout.addLayout(header)

        # Planning panel
        self._tool_plan = QTextEdit(objectName="Sidebar", readOnly=True)
        layout.addWidget(self._tool_plan)

        # Execution panel
        layout.addWidget(QLabel("⚙️ EXECUTION"))
        self._tool_execution = QTextEdit(objectName="Sidebar", readOnly=True)
        layout.addWidget(self._tool_execution)

        self._splitter.addWidget(self._sidebar)

    def _setup_input_area(self) -> None:
        """Setup bottom input area with settings, input field, and submit button."""
        input_box = QWidget()
        layout = QHBoxLayout(input_box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Settings button
        self._settings_btn = QPushButton("⚙️", cursor=Qt.PointingHandCursor)
        self._settings_btn.setObjectName("SettingsButton")
        self._settings_btn.setToolTip("Settings")
        self._settings_btn.setFixedWidth(40)
        self._settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(self._settings_btn)

        # Input field
        self._input_field = QLineEdit(placeholderText="Tell me what to do...")
        self._input_field.returnPressed.connect(self._on_submit)
        layout.addWidget(self._input_field)

        # Submit button
        self._send_btn = QPushButton("Start Task", cursor=Qt.PointingHandCursor)
        self._send_btn.clicked.connect(self._on_submit)
        layout.addWidget(self._send_btn)

        self._main_layout.addWidget(input_box)

    def _create_button(self, text: str, tooltip: str, slot: Callable, obj_name: str) -> QPushButton:
        """Factory method for creating styled buttons."""
        btn = QPushButton(text, toolTip=tooltip, cursor=Qt.PointingHandCursor)
        btn.setObjectName(obj_name)
        btn.clicked.connect(slot)
        return btn

    def _connect_signals(self) -> None:
        """Connect renderer signals to UI update slots."""
        r = self._renderer
        r.new_token_received.connect(self._append_token)
        r.ai_response_start.connect(self._on_ai_response_start)
        r.tool_plan_updated.connect(lambda t: self._update_sidebar(self._tool_plan, t, md=True))
        r.tool_execution_updated.connect(
            lambda t: self._update_sidebar(self._tool_execution, t, md=False)
        )
        r.task_finished.connect(self._on_task_finished)
        r.tool_error_occurred.connect(self._on_tool_error)
        r.fatal_error_occurred.connect(self._on_fatal_error)
        r.captcha_detected.connect(self._on_captcha_detected)
        r.captcha_resolved.connect(self._on_captcha_resolved)

    # --- Responsive Layout ---
    def _apply_responsive_layout(self) -> None:
        """Apply layout configuration based on screen size."""
        cfg = LayoutConfig.for_screen_width(QApplication.primaryScreen().geometry().width())

        self.resize(cfg.width, cfg.height)
        self._main_layout.setContentsMargins(cfg.margins, cfg.margins, cfg.margins, cfg.margins - 8)
        self._main_layout.setSpacing(cfg.spacing)
        self._sidebar.layout().setContentsMargins(cfg.sidebar_margin, 0, 0, 0)
        self._agent_output.setViewportMargins(
            cfg.chat_padding, cfg.chat_padding - 8, cfg.chat_padding, cfg.chat_padding - 8
        )
        self._input_field.setMinimumHeight(cfg.input_height)
        self._send_btn.setFixedSize(cfg.button_width, cfg.input_height)

        self._sidebar_split_ratio = cfg.split_ratio
        if not self._sidebar_manually_hidden:
            self._set_sidebar_visible(cfg.sidebar_visible)

    def _set_sidebar_visible(self, visible: bool) -> None:
        """Set sidebar visibility and update related UI elements."""
        self._sidebar.setVisible(visible)
        self._toggle_btns["show"].setVisible(not visible)
        self._chat_header.setVisible(not visible)
        if visible:
            QTimer.singleShot(0, self._update_splitter_sizes)

    def _update_splitter_sizes(self) -> None:
        """Update splitter sizes based on current ratio."""
        if self._sidebar.isVisible() and (total := self._splitter.width()) > 0:
            self._splitter.setSizes(
                [
                    int(total * self._sidebar_split_ratio[0]),
                    int(total * self._sidebar_split_ratio[1]),
                ]
            )

    def _toggle_sidebar(self) -> None:
        """Toggle sidebar visibility (manual override)."""
        is_visible = self._sidebar.isVisible()
        self._sidebar_manually_hidden = is_visible
        self._set_sidebar_visible(not is_visible)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._sidebar_manually_hidden:
            # Keep show button visible when manually hidden
            self._toggle_btns["show"].setVisible(True)
            self._chat_header.setVisible(True)
        else:
            # Auto-respond to width changes
            should_show = self.width() >= SIDEBAR_AUTO_SHOW_WIDTH
            if self._sidebar.isVisible() != should_show:
                self._set_sidebar_visible(should_show)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close - cleanup resources."""
        if self._cleanup_callback:
            self._cleanup_callback()
        event.accept()

    # --- Chat Logic ---
    def _show_welcome(self) -> None:
        """Display welcome message."""
        self._agent_output.setHtml(WELCOME_HTML)
        self._agent_output.moveCursor(QTextCursor.End)

    def _append_html(self, html: str, new_block: bool = True) -> None:
        """Append HTML content to chat output."""
        cursor = self._agent_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        if new_block and not self._agent_output.document().isEmpty():
            cursor.insertBlock()
        cursor.insertHtml(html)
        self._agent_output.setTextCursor(cursor)
        self._agent_output.ensureCursorVisible()

    @Slot()
    def _on_ai_response_start(self) -> None:
        """Reset AI streaming state for new response."""
        self._ai_header_shown = False
        self._ai_buffer = ""

    @Slot(str)
    def _append_token(self, text: str) -> None:
        """Append streaming AI token to output."""
        if not self._ai_header_shown:
            if not text.strip():
                return
            self._append_html(AI_HEADER_TEMPLATE)
            self._agent_output.append("")
            self._ai_start_pos = self._agent_output.textCursor().position()
            self._ai_buffer = ""
            self._ai_header_shown = True

        self._ai_buffer += text
        cursor = self._agent_output.textCursor()
        cursor.setPosition(self._ai_start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.insertMarkdown(self._ai_buffer)
        self._agent_output.setTextCursor(cursor)
        self._agent_output.ensureCursorVisible()

    @Slot(str, bool)
    def _update_sidebar(self, widget: QTextEdit, text: str, md: bool) -> None:
        """Update sidebar panel content."""
        widget.setMarkdown(text) if md else widget.setPlainText(text)
        widget.moveCursor(QTextCursor.End)

    # --- Task Control ---
    def _set_task_ui_state(self, running: bool, btn_text: str = "Start Task") -> None:
        """Update UI state based on task running status."""
        self._input_field.setEnabled(not running)
        self._settings_btn.setEnabled(not running)
        self._send_btn.setText(btn_text)
        # When running, only enable stop button; when idle, enable submit
        self._send_btn.setEnabled(True)
        if not running:
            self._input_field.setPlaceholderText("Tell me what to do...")
            self._input_field.setFocus()

    def _on_submit(self) -> None:
        """Handle task submission or stop request."""
        if self._is_task_running:
            self._handle_stop_task()
            return

        if text := self._input_field.text().strip():
            self._start_new_task(text)

    def _handle_stop_task(self) -> None:
        """Stop the currently running task."""
        if self._stop_task_callback:
            self._append_html(END_MSG_TEMPLATE.format(icon="🛑", text="Task Stopped."))
            self._send_btn.setText("Stopping")
            self._send_btn.setEnabled(False)
            QApplication.processEvents()
            self._stop_task_callback()
            self._on_task_finished()

    def _start_new_task(self, text: str) -> None:
        """Start a new task with the given input."""
        self._input_field.clear()

        if self._is_first_interaction:
            self._agent_output.clear()
            self._is_first_interaction = False

        self._append_html(USER_MSG_TEMPLATE.format(text=text))
        self._is_task_running = True
        self._set_task_ui_state(running=True, btn_text="Stop Task")
        self._tool_plan.clear()
        self._renderer.reset_state()

        try:
            if self._start_task_callback:
                self._start_task_callback(text)
        except Exception as e:
            self._on_fatal_error(f"Error starting task: {e}")

    @Slot()
    def _on_task_finished(self) -> None:
        """Handle task completion."""
        self._is_task_running = False
        self._agent_output.moveCursor(QTextCursor.End)
        self._set_task_ui_state(running=False)

    @Slot(str)
    def _on_tool_error(self, msg: str) -> None:
        """Handle tool execution error."""
        self._append_html(ERROR_MSG_TEMPLATE.format(text=msg))
        self._agent_output.moveCursor(QTextCursor.End)

    @Slot(str)
    def _on_fatal_error(self, msg: str) -> None:
        """Handle fatal error and reset state."""
        self._is_task_running = False
        self._append_html(ERROR_MSG_TEMPLATE.format(text=msg))
        self._append_html(END_MSG_TEMPLATE.format(icon="❌", text="Task Failed."))
        self._agent_output.moveCursor(QTextCursor.End)
        self._set_task_ui_state(running=False)

    @Slot(str, int, int)
    def _on_captcha_detected(self, engine: str, page_index: int, timeout_ms: int) -> None:
        """Handle captcha detection - notify user that action is required."""
        timeout_sec = timeout_ms // 1000
        msg = (
            f"Please solve {engine.capitalize()} CAPTCHA "
            f"in the browser (Page {page_index}). "
            f"You have <b>{timeout_sec}s</b> to complete it."
        )
        self._append_html(INFO_TEMPLATE.format(icon="🔐", title="CAPTCHA Detected", text=msg))
        self._agent_output.moveCursor(QTextCursor.End)

    @Slot(str, bool)
    def _on_captcha_resolved(self, engine: str, success: bool) -> None:
        """Handle captcha resolution - notify user of the result."""
        if success:
            self._append_html(
                INFO_TEMPLATE.format(
                    icon="🔓",
                    title="CAPTCHA Resolved",
                    text="Please continue your task.",
                )
            )
        else:
            self._append_html(ERROR_MSG_TEMPLATE.format(text="Verification timed out."))
        self._agent_output.moveCursor(QTextCursor.End)

    def _open_settings(self) -> None:
        """Open settings dialog."""
        SettingsDialog(self).exec()
