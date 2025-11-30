import html
import os
from dataclasses import dataclass
from typing import Callable, List, Optional

import markdown
from PySide6.QtCore import Qt, QTimer, QUrl, QUrlQuery, Slot
from PySide6.QtGui import QCloseEvent, QIcon, QResizeEvent, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from hallw.utils import Events, emit

from .history_line_edit import HistoryLineEdit
from .layout_config import LayoutConfig
from .qt_renderer import QtAgentRenderer
from .settings_dialog import SettingsDialog
from .styles import MAIN_STYLE, MARKDOWN_STYLE
from .templates import (
    AI_HEADER_TEMPLATE,
    END_MSG_TEMPLATE,
    ERROR_MSG_TEMPLATE,
    INFO_MSG_TEMPLATE,
    SCRIPT_CONFIRM_OPTIONS_TEMPLATE,
    SCRIPT_CONFIRM_STATUS_TEMPLATE,
    SCRIPT_CONFIRM_TEMPLATE,
    STAGE_MSG_TEMPLATE,
    USER_MSG_TEMPLATE,
    WARNING_MSG_TEMPLATE,
    WELCOME_HTML,
)

# --- Constants ---
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
LOGO_PATH = os.path.join(ASSET_DIR, "logo.ico")
SIDEBAR_AUTO_SHOW_WIDTH = 900


@dataclass
class ChatSegment:
    """Represents a segment of the chat history (HTML or Markdown)."""

    kind: str  # 'html' or 'ai_md'
    content: str
    cached_html: str = ""
    start_pos: int = 0
    end_pos: int = 0


class QtAgentMainWindow(QMainWindow):
    """
    Main application window with chat interface and tool sidebar.
    Optimized for performance with partial rendering and smart scrolling.
    """

    def __init__(
        self,
        renderer: QtAgentRenderer,
        start_task_callback: Callable[[str], None],
        stop_task_callback: Callable[[], None],
        cleanup_callback: Callable[[], None] | None = None,
        reset_callback: Callable[[], None] | None = None,
    ):
        super().__init__()
        self._renderer = renderer
        self._start_task_callback = start_task_callback
        self._stop_task_callback = stop_task_callback
        self._cleanup_callback = cleanup_callback
        self._reset_callback = reset_callback

        # State flags
        self._is_task_running = False
        self._is_first_interaction = True
        self._ai_header_inserted = False
        self._md_style_inserted = False
        self._sidebar_manually_hidden = False
        self._settings_mode: str = ""
        self._handled_script_requests: set[str] = set()
        self._script_request_commands: dict[str, str] = {}
        self._script_request_segments: dict[str, int] = {}

        # Chat render state
        self._segments: List[ChatSegment] = []
        self._current_ai_index: Optional[int] = None

        # Position tracker for partial updates (Optimization: Partial Refresh)
        self._current_response_start_pos: int = 0
        self._current_response_end_pos: int = 0

        # AI streaming state
        self._stream_update_pending = False

        # Streaming throttle (approx 25 FPS)
        self._stream_timer = QTimer(self)
        self._stream_timer.setInterval(40)
        self._stream_timer.timeout.connect(self._flush_stream_buffer)
        self._stream_timer.start()

        # UI Components
        self._splitter: QSplitter
        self._chat_header: QWidget
        self._agent_output: QTextBrowser
        self._tool_plan: QTextEdit
        self._tool_execution: QTextEdit
        self._input_field: HistoryLineEdit
        self._send_btn: QPushButton
        self._settings_btn: QPushButton
        self._sidebar: QWidget
        self._toggle_btns: dict[str, QPushButton] = {}
        self._sidebar_split_ratio: tuple[float, float] = (0.8, 0.2)

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

        # Chat Header
        self._chat_header = QWidget()
        header_layout = QHBoxLayout(self._chat_header)
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.addStretch()
        self._toggle_btns["show"] = self._create_button("◨", "Show Sidebar", self._toggle_sidebar, "ShowSidebar")
        header_layout.addWidget(self._toggle_btns["show"])
        chat_layout.addWidget(self._chat_header)

        # Chat Output Area
        self._agent_output = QTextBrowser()
        self._agent_output.setReadOnly(True)
        self._agent_output.setOpenLinks(False)
        self._agent_output.setOpenExternalLinks(False)
        self._agent_output.anchorClicked.connect(self._on_anchor_clicked)
        chat_layout.addWidget(self._agent_output)
        self._splitter.addWidget(chat_container)

    def _setup_sidebar(self) -> None:
        """Setup right sidebar with planning and execution panels."""
        self._sidebar = QWidget()
        layout = QVBoxLayout(self._sidebar)

        header = QHBoxLayout()
        header.addWidget(QLabel("📋 PLANNING"))
        header.addStretch()
        self._toggle_btns["hide"] = self._create_button("◧", "Hide Sidebar", self._toggle_sidebar, "HideSidebar")
        header.addWidget(self._toggle_btns["hide"])
        layout.addLayout(header)

        self._tool_plan = QTextEdit(objectName="Sidebar", readOnly=True)
        layout.addWidget(self._tool_plan)

        layout.addWidget(QLabel("⚙️ EXECUTION"))
        self._tool_execution = QTextEdit(objectName="Sidebar", readOnly=True)
        layout.addWidget(self._tool_execution)

        self._splitter.addWidget(self._sidebar)

    def _setup_input_area(self) -> None:
        """Setup bottom input area."""
        input_box = QWidget()
        layout = QHBoxLayout(input_box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._settings_btn = QPushButton(cursor=Qt.PointingHandCursor)
        self._settings_btn.setObjectName("SettingsButton")
        self._settings_btn.setFixedWidth(40)
        layout.addWidget(self._settings_btn)
        self._settings_btn.setText("⚙️")
        self._settings_btn.setToolTip("Settings")
        self._settings_btn.clicked.connect(lambda: SettingsDialog(self).exec())

        # Use custom HistoryLineEdit
        self._input_field = HistoryLineEdit()
        self._input_field.setPlaceholderText("Tell me what to do...")
        self._input_field.returnPressed.connect(self._on_submit)
        layout.addWidget(self._input_field)

        self._send_btn = QPushButton("Send", cursor=Qt.PointingHandCursor)
        self._send_btn.setObjectName("SendButton")
        self._send_btn.clicked.connect(self._on_submit)
        layout.addWidget(self._send_btn)

        self._main_layout.addWidget(input_box)

    def _connect_signals(self) -> None:
        """Connect renderer signals to UI update slots."""
        r = self._renderer
        r.new_token_received.connect(self._append_token)
        r.ai_response_start.connect(self._on_ai_response_start)
        r.tool_plan_updated.connect(lambda t: self._update_sidebar(self._tool_plan, t, md=True))
        r.tool_execution_updated.connect(lambda t: self._update_sidebar(self._tool_execution, t, md=False))
        r.task_finished.connect(self._on_task_finished)
        r.tool_error_occurred.connect(self._on_tool_error)
        r.fatal_error_occurred.connect(self._on_fatal_error)
        r.captcha_detected.connect(self._on_captcha_detected)
        r.captcha_resolved.connect(self._on_captcha_resolved)
        r.stage_started.connect(self._on_stage_started)
        r.script_confirm_requested.connect(self._on_script_confirm)

    # --- UI Helpers ---
    def _show_welcome(self) -> None:
        """Display welcome message and reset state."""
        self._segments.clear()
        self._current_ai_index = None
        self._agent_output.setHtml(WELCOME_HTML)
        self._agent_output.moveCursor(QTextCursor.End)

    def _create_button(self, text: str, tooltip: str, slot: Callable, obj_name: str) -> QPushButton:
        btn = QPushButton(text, toolTip=tooltip, cursor=Qt.PointingHandCursor)
        btn.setObjectName(obj_name)
        btn.clicked.connect(slot)
        return btn

    def _set_settings_button_mode(self, mode: str) -> None:
        """Toggle the settings button between 'settings' and 'back/reset' mode."""
        if mode == self._settings_mode:
            return

        try:
            self._settings_btn.clicked.disconnect()
        except TypeError:
            pass

        if mode == "settings":
            self._settings_btn.setText("⚙️")
            self._settings_btn.setToolTip("Settings")
            self._settings_btn.clicked.connect(lambda: SettingsDialog(self).exec())
        else:
            self._settings_btn.setText("↩️")
            self._settings_btn.setToolTip("Back to start")
            self._settings_btn.clicked.connect(self._reset_session)

        self._settings_mode = mode

    # --- Smart Scrolling Helpers ---
    def _check_if_user_at_bottom(self) -> bool:
        """
        Checks if the vertical scrollbar is effectively at the bottom BEFORE
        new content is inserted. Tolerance is 20 pixels.
        """
        scrollbar = self._agent_output.verticalScrollBar()
        return int(scrollbar.value()) >= int(scrollbar.maximum() - 20)

    def _force_scroll_to_bottom(self) -> None:
        """Forces the scrollbar to the absolute bottom."""
        scrollbar = self._agent_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _append_html(self, html_content: str) -> None:
        """
        Appends a pre-rendered HTML segment directly to the QTextEdit.
        Updates the segment list for state persistence.
        """
        # 1. Capture scroll state BEFORE insertion
        was_at_bottom = self._check_if_user_at_bottom()

        # Update UI incrementally (Optimization: Partial Refresh)
        cursor = self._agent_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        start_pos = cursor.position()
        cursor.insertHtml(html_content)
        end_pos = cursor.position()

        # Store state with positions
        self._segments.append(ChatSegment(kind="html", content=html_content, start_pos=start_pos, end_pos=end_pos))

        # 2. Scroll AFTER insertion only if user was already at bottom
        if was_at_bottom:
            self._force_scroll_to_bottom()

    def _append_user_message(self, text: str) -> None:
        """Sanitizes and appends a user message."""
        safe_text = html.escape(text)
        html_block = USER_MSG_TEMPLATE.format(text=safe_text)
        self._append_html(html_block)

    # --- Responsive Layout ---
    def _apply_responsive_layout(self) -> None:
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
        self._sidebar.setVisible(visible)
        self._toggle_btns["show"].setVisible(not visible)
        self._chat_header.setVisible(not visible)
        if visible:
            QTimer.singleShot(0, self._update_splitter_sizes)

    def _update_splitter_sizes(self) -> None:
        if self._sidebar.isVisible() and (total := self._splitter.width()) > 0:
            self._splitter.setSizes(
                [
                    int(total * self._sidebar_split_ratio[0]),
                    int(total * self._sidebar_split_ratio[1]),
                ]
            )

    def _toggle_sidebar(self) -> None:
        is_visible = self._sidebar.isVisible()
        self._sidebar_manually_hidden = is_visible
        self._set_sidebar_visible(not is_visible)

    # --- Window Events ---
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._sidebar_manually_hidden:
            self._toggle_btns["show"].setVisible(True)
            self._chat_header.setVisible(True)
        else:
            should_show = self.width() >= SIDEBAR_AUTO_SHOW_WIDTH
            if self._sidebar.isVisible() != should_show:
                self._set_sidebar_visible(should_show)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._cleanup_callback:
            self._cleanup_callback()
        event.accept()

    # --- Task / Interaction Logic ---
    def _on_submit(self) -> None:
        if self._is_task_running:
            self._handle_stop_task()
            return

        text = self._input_field.text().strip()
        if text:
            self._input_field.add_to_history(text)
            self._start_new_task(text)

    def _handle_stop_task(self) -> None:
        if self._stop_task_callback:
            self._append_html(END_MSG_TEMPLATE.format(icon="🛑", text="Task Stopped."))
            self._send_btn.setText("Stopping")
            self._send_btn.setEnabled(False)
            QApplication.processEvents()
            self._stop_task_callback()
            self._on_task_finished()

    def _start_new_task(self, text: str) -> None:
        self._input_field.clear()

        if self._is_first_interaction:
            self._segments.clear()
            self._agent_output.clear()
            self._is_first_interaction = False

        self._set_settings_button_mode("back")
        self._stream_update_pending = False
        self._current_ai_index = None
        self._append_user_message(text)
        self._is_task_running = True
        self._set_task_ui_state(running=True)
        self._tool_plan.clear()

        try:
            if self._start_task_callback:
                self._start_task_callback(text)
        except Exception as e:
            self._on_fatal_error(f"Error starting task: {e}")

    # --- AI Streaming Logic ---
    @Slot()
    def _on_ai_response_start(self) -> None:
        """
        Initializes a new AI response segment.
        Records the cursor position to enable efficient partial updates.
        """
        # If a previous response was mid-stream, render it before starting a new one
        self._flush_stream_buffer(force=True)
        self._stream_update_pending = False
        self._ai_header_inserted = False

        # Create a new segment tracker
        self._segments.append(ChatSegment(kind="ai_md", content=""))
        self._current_ai_index = len(self._segments) - 1

    @Slot(str)
    def _append_token(self, text: str) -> None:
        """Buffers incoming tokens. UI update is handled by timer."""
        if self._current_ai_index is None:
            self._on_ai_response_start()

        if not text.strip():
            return

        # Only insert on first real token
        if not self._ai_header_inserted:
            self._append_html(AI_HEADER_TEMPLATE)
            self._ai_header_inserted = True

            # Record start pos for partial updates
            cursor = self._agent_output.textCursor()
            cursor.movePosition(QTextCursor.End)
            pos = cursor.position()
            self._current_response_start_pos = pos
            self._current_response_end_pos = pos

        idx = self._current_ai_index
        if idx is not None and idx < len(self._segments):
            self._segments[idx].content += text
            self._stream_update_pending = True

    def _flush_stream_buffer(self, force: bool = False) -> None:
        """Flush streaming buffer by updating ONLY the active AI block."""
        if not force and not self._stream_update_pending:
            return

        self._stream_update_pending = False
        self._render_last_segment()

    def _render_last_segment(self) -> None:
        """
        Incrementally re-renders the latest AI markdown segment.
        """
        idx = self._current_ai_index
        if idx is None or idx >= len(self._segments):
            return

        # 1. Capture scroll state BEFORE text modification
        # This fixes the issue where 'maximum' grows before we check 'value'.
        was_at_bottom = self._check_if_user_at_bottom()

        seg = self._segments[idx]
        md_text = seg.content

        # Render Markdown to HTML
        html_body = markdown.markdown(
            md_text,
            extensions=["fenced_code", "tables"],
            output_format="html5",
        )

        # Partial Refresh using Cursor
        cursor = self._agent_output.textCursor()
        start_pos = self._current_response_start_pos
        end_pos = max(self._current_response_end_pos, start_pos)
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        cursor.insertHtml(f"<style>{MARKDOWN_STYLE}</style>{html_body}")
        self._current_response_end_pos = cursor.position()

        # 2. Force scroll AFTER modification only if user was previously at bottom
        if was_at_bottom:
            self._force_scroll_to_bottom()

    # --- Sidebar Logic ---
    def _update_sidebar(self, widget: QTextEdit, text: str, md: bool) -> None:
        if md:
            widget.setHtml(self._render_markdown_to_html(text))
        else:
            widget.setPlainText(text)
        widget.moveCursor(QTextCursor.End)

    # --- Task End / Error ---
    @Slot()
    def _on_task_finished(self) -> None:
        self._is_task_running = False
        self._flush_stream_buffer()
        self._agent_output.moveCursor(QTextCursor.End)
        self._set_task_ui_state(running=False)

    @Slot(str)
    def _on_tool_error(self, msg: str) -> None:
        self._append_html(ERROR_MSG_TEMPLATE.format(text=msg))

    @Slot(str)
    def _on_fatal_error(self, msg: str) -> None:
        self._is_task_running = False
        self._append_html(ERROR_MSG_TEMPLATE.format(text=msg))
        self._append_html(END_MSG_TEMPLATE.format(icon="❌", text="Task Failed."))
        self._set_task_ui_state(running=False)

    @Slot(str, int, int)
    def _on_captcha_detected(self, engine: str, page_index: int, timeout_ms: int) -> None:
        timeout_sec = timeout_ms // 1000
        msg = (
            f"{engine.capitalize()} CAPTCHA detected "
            f"in the browser (Page {page_index + 1}). "
            f"Please solve it in <b>{timeout_sec}s</b>."
        )
        self._append_html(WARNING_MSG_TEMPLATE.format(text=msg))

    @Slot(str, bool)
    def _on_captcha_resolved(self, engine: str, success: bool) -> None:
        if success:
            html_block = INFO_MSG_TEMPLATE.format(
                icon="🔓",
                title="CAPTCHA Resolved",
                text="Please continue your task.",
            )
            self._append_html(html_block)
        else:
            self._append_html(ERROR_MSG_TEMPLATE.format(text="Verification timed out."))

    @Slot(int, int, str)
    def _on_stage_started(self, stage_index: int, total_stages: int, stage_name: str) -> None:
        self._append_html(STAGE_MSG_TEMPLATE.format(title=f"Stage {stage_index + 1}/{total_stages}", text=stage_name))

    @Slot(str, str)
    def _on_script_confirm(self, request_id: str, command: str) -> None:
        """Render script execution confirmation request."""
        if not request_id:
            return

        self._handled_script_requests.discard(request_id)
        self._script_request_commands[request_id] = command or ""
        html_block = self._build_script_confirm_card(request_id, command)
        self._append_html(html_block)
        self._script_request_segments[request_id] = len(self._segments) - 1

    def _build_script_confirm_card(self, request_id: str, command: str) -> str:
        approve_url = f"hallw://script-confirm?request_id={request_id}&decision=approve"
        reject_url = f"hallw://script-confirm?request_id={request_id}&decision=reject"
        safe_command = html.escape(command) if command else "(empty command)"
        options_bar = SCRIPT_CONFIRM_OPTIONS_TEMPLATE.format(
            approve_url=approve_url,
            reject_url=reject_url,
        )
        return SCRIPT_CONFIRM_TEMPLATE.format(command=safe_command, notice=options_bar)

    def _build_script_decision_card(self, request_id: str, approved: bool) -> str:
        command = self._script_request_commands.pop(request_id, "")
        status = "APPROVED" if approved else "REJECTED"
        safe_command = html.escape(command) if command else "(empty command)"
        status_bar = SCRIPT_CONFIRM_STATUS_TEMPLATE.format(text=status)
        return SCRIPT_CONFIRM_TEMPLATE.format(command=safe_command, notice=status_bar)

    def _replace_html_segment(self, seg_idx: int, new_html: str) -> bool:
        """Replace an existing HTML segment in-place without rerendering the whole document."""
        if seg_idx < 0 or seg_idx >= len(self._segments):
            return False

        seg = self._segments[seg_idx]
        if seg.kind != "html":
            return False

        start = seg.start_pos
        end = seg.end_pos
        if start < 0 or end < start:
            return False

        cursor = self._agent_output.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        cursor.insertHtml(new_html)
        new_end = cursor.position()

        delta = new_end - end
        seg.content = new_html
        seg.end_pos = new_end

        # Shift subsequent segments to keep positions accurate
        if delta != 0:
            for i in range(seg_idx + 1, len(self._segments)):
                s = self._segments[i]
                s.start_pos += delta
                s.end_pos += delta

        # Adjust streaming cursor anchors if they live after this segment
        if self._current_response_start_pos > end:
            self._current_response_start_pos += delta
            self._current_response_end_pos += delta

        self._force_scroll_to_bottom()
        return True

    @Slot(QUrl)
    def _on_anchor_clicked(self, url: QUrl) -> None:
        """Handle custom action links inside the chat view (e.g., script approval)."""
        if url.scheme() != "hallw" or url.host() != "script-confirm":
            return

        query = QUrlQuery(url)
        request_id = query.queryItemValue("request_id")
        decision = query.queryItemValue("decision")

        if not request_id or not decision or request_id in self._handled_script_requests:
            return

        approved = decision == "approve"
        self._handled_script_requests.add(request_id)
        replaced = False

        if request_id in self._script_request_segments:
            seg_idx = self._script_request_segments.pop(request_id)
            new_html = self._build_script_decision_card(request_id, approved)
            replaced = self._replace_html_segment(seg_idx, new_html)

        if not replaced:
            # Fallback: append a new notice card if we can't locate/replace the original
            self._append_html(self._build_script_decision_card(request_id, approved))

        emit(
            Events.SCRIPT_CONFIRM_RESPONDED,
            {"request_id": request_id, "approved": approved},
        )

    # --- Helpers ---
    def _set_task_ui_state(self, running: bool) -> None:
        self._input_field.setEnabled(not running)
        self._settings_btn.setEnabled(not running)
        self._send_btn.setEnabled(True)

        self._settings_btn.setText("↩️" if not running else "⏳")
        self._send_btn.setText("Stop" if running else "Send")

        if not running:
            self._input_field.setPlaceholderText("Tell me what to do...")
            self._input_field.setFocus()

    def _reset_session(self) -> None:
        """Resets the UI and Renderer state to the initial welcome screen."""
        if self._is_task_running and self._stop_task_callback:
            try:
                self._stop_task_callback()
            except Exception:
                pass

        if self._reset_callback:
            try:
                self._reset_callback()
            except Exception:
                pass

        self._is_task_running = False
        self._is_first_interaction = True
        self._sidebar_manually_hidden = False
        self._stream_update_pending = False
        self._current_ai_index = None
        self._current_response_start_pos = 0
        self._current_response_end_pos = 0
        self._handled_script_requests.clear()
        self._script_request_commands.clear()
        self._script_request_segments.clear()

        self._renderer.reset_state()
        self._segments.clear()
        self._agent_output.clear()
        self._tool_plan.clear()
        self._tool_execution.clear()
        self._show_welcome()

        self._set_task_ui_state(running=False)
        self._set_settings_button_mode("settings")
        self._set_sidebar_visible(True)
        self._input_field.clear()

    def _render_markdown_to_html(self, text: str) -> str:
        """Helper for non-streamed markdown rendering (e.g. Sidebar)."""
        if not text.strip():
            return ""

        html_body = markdown.markdown(
            text,
            extensions=["fenced_code", "tables"],
            output_format="html5",
        )

        return f"<style>{MARKDOWN_STYLE}</style>{html_body}"
