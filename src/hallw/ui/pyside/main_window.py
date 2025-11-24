import os
import queue
from dataclasses import dataclass
from typing import Callable, Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QIcon, QTextCursor
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

import hallw.tools.ask_info

from .qt_renderer import QtAgentRenderer
from .styles import STYLE
from .templates import (
    AI_HEADER_TEMPLATE,
    END_MSG_TEMPLATE,
    ERROR_MSG_TEMPLATE,
    LAUNCH_MSG_TEMPLATE,
    QUESTION_MSG_TEMPLATE,
    USER_MSG_TEMPLATE,
    WELCOME_HTML,
)

# --- Global / Constants ---
INPUT_QUEUE: queue.Queue = queue.Queue()
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSET_DIR, "logo.ico")


def gui_get_user_input(timeout: int = None) -> Optional[str]:
    try:
        return str(INPUT_QUEUE.get(timeout=timeout))
    except queue.Empty:
        return None


hallw.tools.ask_info.get_user_input = gui_get_user_input


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
    split_ratio: list[float]


class QtAgentMainWindow(QMainWindow):
    def __init__(self, renderer: QtAgentRenderer, start_task_callback: Callable[[str], None]):
        super().__init__()
        self.renderer = renderer
        self.start_task_callback = start_task_callback

        # State
        self.is_waiting_for_response = False
        self.is_first_interaction = True
        self.has_error = False
        self.sidebar_manually_hidden = False
        self.ai_buffer = ""
        self.ai_start_pos = 0
        self.countdown = 60

        # UI Components Placeholders
        self.splitter: QSplitter
        self.chat_header: QWidget
        self.agent_output: QTextEdit
        self.tool_plan: QTextEdit
        self.tool_execution: QTextEdit
        self.input_field: QLineEdit
        self.send_btn: QPushButton
        self.sidebar: QWidget
        self.toggle_btns: dict[str, QPushButton] = {}

        self._init_window()
        self._setup_ui()
        self._connect_signals()

        # Apply initial responsive state
        self._apply_responsive_layout()
        self._init_welcome()

    def _init_window(self):
        self.setWindowTitle("HALLW")
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))
        self.setStyleSheet(STYLE)
        self.input_timer = QTimer(self)
        self.input_timer.timeout.connect(self._on_countdown_tick)

    def _setup_ui(self):
        """Setup main UI components and layout."""
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)

        # 1. Main Splitter Area
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)
        self.main_layout.addWidget(self.splitter, stretch=1)

        # Left: Chat
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Chat Header (Toggle Button)
        self.chat_header = QWidget()
        ch_layout = QHBoxLayout(self.chat_header)
        ch_layout.setContentsMargins(0, 0, 0, 4)
        ch_layout.addStretch()
        self.toggle_btns["show"] = self._create_btn(
            "◨", "Show Sidebar", self.toggle_sidebar, obj_name="ShowSidebar"
        )
        ch_layout.addWidget(self.toggle_btns["show"])
        chat_layout.addWidget(self.chat_header)

        self.agent_output = QTextEdit(readOnly=True)
        chat_layout.addWidget(self.agent_output)
        self.splitter.addWidget(chat_container)

        # Right: Sidebar
        self.sidebar = QWidget()
        sb_layout = QVBoxLayout(self.sidebar)

        # Sidebar Header
        sb_header = QHBoxLayout()
        sb_header.addWidget(QLabel("📋 PLANNING"))
        sb_header.addStretch()
        self.toggle_btns["hide"] = self._create_btn(
            "◧", "Hide Sidebar", self.toggle_sidebar, obj_name="HideSidebar"
        )
        sb_header.addWidget(self.toggle_btns["hide"])

        sb_layout.addLayout(sb_header)
        self.tool_plan = QTextEdit(objectName="Sidebar", readOnly=True)
        sb_layout.addWidget(self.tool_plan)
        sb_layout.addWidget(QLabel("⚙️ EXECUTION"))
        self.tool_execution = QTextEdit(objectName="Sidebar", readOnly=True)
        sb_layout.addWidget(self.tool_execution)
        self.splitter.addWidget(self.sidebar)

        # 2. Bottom Input Area
        input_box = QWidget()
        self.input_layout = QHBoxLayout(input_box)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setSpacing(12)

        self.input_field = QLineEdit(placeholderText="Tell me what to do...")
        self.input_field.returnPressed.connect(self.on_submit)
        self.input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Start Task", cursor=Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self.on_submit)
        self.input_layout.addWidget(self.send_btn)

        self.main_layout.addWidget(input_box)

    def _create_btn(
        self, text: str, tooltip: str, slot: Callable, obj_name: str = None
    ) -> QPushButton:
        btn = QPushButton(text, toolTip=tooltip, cursor=Qt.PointingHandCursor)
        btn.setObjectName(obj_name)
        btn.clicked.connect(slot)
        return btn

    def _connect_signals(self):
        r = self.renderer
        r.new_token_received.connect(self._append_token)
        r.ai_response_start.connect(self._start_ai_response)
        r.tool_plan_updated.connect(lambda t: self._update_sidebar_text(self.tool_plan, t, md=True))
        r.tool_execution_updated.connect(
            lambda t: self._update_sidebar_text(self.tool_execution, t, md=False)
        )
        r.request_input.connect(self._enable_input_mode)
        r.task_finished.connect(self._on_finished)
        r.tool_error_occurred.connect(self._on_tool_error)
        r.fatal_error_occurred.connect(self._on_fatal_error)

    # --- Responsive Logic ---
    def _get_layout_config(self) -> LayoutConfig:
        w = QApplication.primaryScreen().geometry().width()
        if w < 1024:
            return LayoutConfig(
                width=min(900, int(w * 0.9)),
                height=700,
                sidebar_visible=False,
                margins=20,
                spacing=16,
                chat_padding=20,
                sidebar_margin=15,
                input_height=52,
                button_width=120,
                split_ratio=[1.0, 0.0],
            )
        elif w < 1366:
            return LayoutConfig(
                width=1100,
                height=750,
                sidebar_visible=True,
                margins=28,
                spacing=20,
                chat_padding=24,
                sidebar_margin=16,
                input_height=56,
                button_width=130,
                split_ratio=[0.72, 0.28],
            )
        else:
            return LayoutConfig(
                width=1200,
                height=800,
                sidebar_visible=True,
                margins=32,
                spacing=24,
                chat_padding=28,
                sidebar_margin=18,
                input_height=60,
                button_width=140,
                split_ratio=[0.74, 0.26],
            )

    def _apply_responsive_layout(self):
        cfg = self._get_layout_config()

        # Window & Layout
        self.resize(cfg.width, cfg.height)
        self.main_layout.setContentsMargins(cfg.margins, cfg.margins, cfg.margins, cfg.margins - 8)
        self.main_layout.setSpacing(cfg.spacing)

        # Sidebar Content Margins
        self.sidebar.layout().setContentsMargins(cfg.sidebar_margin, 0, 0, 0)

        # Chat Padding
        self.agent_output.setViewportMargins(
            cfg.chat_padding, cfg.chat_padding - 8, cfg.chat_padding, cfg.chat_padding - 8
        )

        # Input Sizes
        self.input_field.setMinimumHeight(cfg.input_height)
        self.send_btn.setFixedSize(cfg.button_width, cfg.input_height)

        # Visibility & Splitter
        self.sidebar_split_ratio = cfg.split_ratio
        if not self.sidebar_manually_hidden:
            self._set_sidebar_state(cfg.sidebar_visible)

    def _set_sidebar_state(self, visible: bool):
        self.sidebar.setVisible(visible)
        self.toggle_btns["show"].setVisible(not visible)
        self.chat_header.setVisible(not visible)
        if visible:
            QTimer.singleShot(0, self._update_splitter)

    def _update_splitter(self):
        if self.sidebar.isVisible() and self.splitter.width() > 0:
            total = self.splitter.width()
            self.splitter.setSizes(
                [int(total * self.sidebar_split_ratio[0]), int(total * self.sidebar_split_ratio[1])]
            )

    def toggle_sidebar(self):
        is_visible = self.sidebar.isVisible()
        self.sidebar_manually_hidden = is_visible
        self._set_sidebar_state(not is_visible)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Only auto-respond if not manually overridden
        if not self.sidebar_manually_hidden:
            should_show = self.width() >= 900
            if self.sidebar.isVisible() != should_show:
                self._set_sidebar_state(should_show)
        else:
            # Ensure the show button is always visible when manually hidden
            self.toggle_btns["show"].setVisible(True)
            self.chat_header.setVisible(True)

    # --- Chat Logic ---
    def _init_welcome(self):
        self.agent_output.setHtml(WELCOME_HTML)
        self.agent_output.moveCursor(QTextCursor.End)

    def _append_html(self, html: str, new_block: bool = True):
        cursor = self.agent_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        if new_block and not self.agent_output.document().isEmpty():
            cursor.insertBlock()
        cursor.insertHtml(html)
        self.agent_output.setTextCursor(cursor)
        self.agent_output.ensureCursorVisible()

    @Slot()
    def _start_ai_response(self):
        self._append_html(AI_HEADER_TEMPLATE)
        self.agent_output.append("")
        self.ai_start_pos = self.agent_output.textCursor().position()
        self.ai_buffer = ""

    @Slot(str)
    def _append_token(self, text: str):
        self.ai_buffer += text
        cursor = self.agent_output.textCursor()
        cursor.setPosition(self.ai_start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.insertMarkdown(self.ai_buffer)
        self.agent_output.setTextCursor(cursor)
        self.agent_output.ensureCursorVisible()

    @Slot(str, bool)
    def _update_sidebar_text(self, widget: QTextEdit, text: str, md: bool):
        if md:
            widget.setMarkdown(text)
        else:
            widget.setPlainText(text)
        widget.moveCursor(QTextCursor.End)

    @Slot(str)
    def _enable_input_mode(self, question: str):
        self._append_html(QUESTION_MSG_TEMPLATE.format(text=question))
        self.is_waiting_for_response = True
        self.countdown = 60
        self._set_input_enabled(True, "Reply")
        self.input_field.setFocus()
        self.input_timer.start(1000)

    def _on_countdown_tick(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self.input_timer.stop()
            self.input_field.setPlaceholderText("Timeout...")
            self._set_input_enabled(False)
        else:
            self.input_field.setPlaceholderText(f"Say something... ({self.countdown}s)")

    def _set_input_enabled(self, enabled: bool, btn_text: str = None):
        self.input_field.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)
        if btn_text:
            self.send_btn.setText(btn_text)

    def on_submit(self):
        text = self.input_field.text().strip()
        if not text:
            return

        self.input_field.clear()
        self.has_error = False

        if self.is_first_interaction:
            self.agent_output.clear()
            self.is_first_interaction = False

        self._append_html(USER_MSG_TEMPLATE.format(text=text))

        if self.is_waiting_for_response:
            self.input_timer.stop()
            INPUT_QUEUE.put(text)
            self.is_waiting_for_response = False
            self.input_field.setPlaceholderText("Processing...")
            self._set_input_enabled(False)
        else:
            self._set_input_enabled(False)
            self.tool_plan.clear()
            self.tool_execution.clear()
            self.renderer.reset_state()
            self._append_html(LAUNCH_MSG_TEMPLATE.format(text="Task Launching..."))
            try:
                if self.start_task_callback:
                    self.start_task_callback(text)
            except Exception as e:
                self._on_fatal_error(f"Error starting task: {e}")

    @Slot()
    def _on_finished(self):
        if not self.has_error:
            self._append_html(END_MSG_TEMPLATE.format(icon="✅", text="Task Completed."))
        self._set_input_enabled(True, "Start Task")
        self.input_field.setPlaceholderText("Tell me what to do...")
        self.input_field.setFocus()

    @Slot(str)
    def _on_tool_error(self, msg: str):
        self.has_error = True
        self._append_html(ERROR_MSG_TEMPLATE.format(text=msg))
        self.agent_output.moveCursor(QTextCursor.End)

    @Slot(str)
    def _on_fatal_error(self, msg: str):
        self.has_error = True
        self._append_html(ERROR_MSG_TEMPLATE.format(text=f"{msg}"))
        self._append_html(END_MSG_TEMPLATE.format(icon="❌", text="Task Failed."))
        self.agent_output.moveCursor(QTextCursor.End)
        self._set_input_enabled(True, "Start Task")
        self.input_field.setPlaceholderText("Tell me what to do...")
        self.input_field.setFocus()
