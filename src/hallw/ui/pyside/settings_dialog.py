import os
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from hallw.utils.config_mgr import config, reload_config

from .styles import SETTINGS_STYLE


class FieldType(Enum):
    """Field types for settings."""

    TEXT = "text"
    PASSWORD = "password"
    CHECKBOX = "checkbox"
    COMBO = "combo"


@dataclass
class FieldDef:
    """Definition for a settings field."""

    label: str  # Display label
    env_key: str  # Environment variable key
    config_attr: str  # Pydantic config attribute name
    field_type: FieldType = FieldType.TEXT
    options: list[str] | None = None  # For combo boxes


# Tab definitions with their fields
TAB_DEFINITIONS: dict[str, list[FieldDef]] = {
    "Model": [
        FieldDef("Model Name:", "MODEL_NAME", "model_name"),
        FieldDef("Endpoint:", "MODEL_ENDPOINT", "model_endpoint"),
        FieldDef("API Key:", "MODEL_API_KEY", "model_api_key", FieldType.PASSWORD),
        FieldDef("Temperature:", "MODEL_TEMPERATURE", "model_temperature"),
        FieldDef("Max Output Tokens:", "MODEL_MAX_OUTPUT_TOKENS", "model_max_output_tokens"),
        FieldDef(
            "Reflection Threshold:", "MODEL_REFLECTION_THRESHOLD", "model_reflection_threshold"
        ),
        FieldDef("Max Recursion:", "MODEL_MAX_RECURSION", "model_max_recursion"),
    ],
    "LangSmith": [
        FieldDef("Enable Tracing:", "LANGSMITH_TRACING", "langsmith_tracing", FieldType.CHECKBOX),
        FieldDef("Endpoint:", "LANGSMITH_ENDPOINT", "langsmith_endpoint"),
        FieldDef("API Key:", "LANGSMITH_API_KEY", "langsmith_api_key", FieldType.PASSWORD),
        FieldDef("Project:", "LANGSMITH_PROJECT", "langsmith_project"),
    ],
    "Logging": [
        FieldDef(
            "Logging Level:",
            "LOGGING_LEVEL",
            "logging_level",
            FieldType.COMBO,
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        ),
        FieldDef("Log Directory:", "LOGGING_FILE_DIR", "logging_file_dir"),
        FieldDef("Max Message Chars:", "MAX_MESSAGE_CHARS", "max_message_chars"),
    ],
    "Browser": [
        FieldDef(
            "Prefer Local Chrome:", "PREFER_LOCAL_CHROME", "prefer_local_chrome", FieldType.CHECKBOX
        ),
        FieldDef("Chrome User Data Dir:", "CHROME_USER_DATA_DIR", "chrome_user_data_dir"),
        FieldDef("CDP Port:", "CDP_PORT", "cdp_port"),
        FieldDef("Headless Mode:", "PW_HEADLESS_MODE", "pw_headless_mode", FieldType.CHECKBOX),
        FieldDef("Window Width:", "PW_WINDOW_WIDTH", "pw_window_width"),
        FieldDef("Window Height:", "PW_WINDOW_HEIGHT", "pw_window_height"),
        FieldDef(
            "Keep Browser Open:", "KEEP_BROWSER_OPEN", "keep_browser_open", FieldType.CHECKBOX
        ),
        FieldDef(
            "Search Engine:",
            "BROWSER_SEARCH_ENGINE",
            "browser_search_engine",
            FieldType.COMBO,
            ["Google", "Bing", "Baidu"],
        ),
        FieldDef("Search Result Count:", "SEARCH_RESULT_COUNT", "search_result_count"),
        FieldDef("Max Page Content Chars:", "MAX_PAGE_CONTENT_CHARS", "max_page_content_chars"),
        FieldDef(
            "Manual Captcha Timeout (ms):", "MANUAL_CAPTCHA_TIMEOUT", "manual_captcha_timeout"
        ),
        FieldDef("Goto Timeout (ms):", "PW_GOTO_TIMEOUT", "pw_goto_timeout"),
        FieldDef("Click Timeout (ms):", "PW_CLICK_TIMEOUT", "pw_click_timeout"),
        FieldDef("CDP Timeout (ms):", "PW_CDP_TIMEOUT", "pw_cdp_timeout"),
    ],
    "File": [
        FieldDef("Read Directory:", "FILE_READ_DIR", "file_read_dir"),
        FieldDef("Save Directory:", "FILE_SAVE_DIR", "file_save_dir"),
        FieldDef("Max Read Chars:", "FILE_MAX_READ_CHARS", "file_max_read_chars"),
    ],
}

# Tabs that need scroll area
SCROLLABLE_TABS = {"Browser"}


class SettingsDialog(QDialog):
    """Settings dialog with tabbed configuration panels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(700, 800)
        self.setStyleSheet(SETTINGS_STYLE)

        self._widgets: dict[str, QWidget] = {}  # env_key -> widget
        self._init_ui()
        self._load_values()

    def _init_ui(self) -> None:
        """Initialize the UI with tabs and fields."""
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        for tab_name, fields in TAB_DEFINITIONS.items():
            tab_widget = self._create_tab(fields)
            if tab_name in SCROLLABLE_TABS:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(tab_widget)
                tabs.addTab(scroll, tab_name)
            else:
                tabs.addTab(tab_widget, tab_name)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_and_close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _create_tab(self, fields: list[FieldDef]) -> QWidget:
        """Create a tab widget with form fields."""
        tab = QWidget()
        tab.setObjectName("TabContent")
        form = QFormLayout(tab)

        for field in fields:
            widget = self._create_field_widget(field)
            self._widgets[field.env_key] = widget
            form.addRow(field.label, widget)

        return tab

    def _create_field_widget(self, field: FieldDef) -> QWidget:
        """Create the appropriate widget for a field type."""
        match field.field_type:
            case FieldType.PASSWORD:
                widget = QLineEdit()
                widget.setEchoMode(QLineEdit.Password)
            case FieldType.CHECKBOX:
                widget = QCheckBox()
            case FieldType.COMBO:
                widget = QComboBox()
                if field.options:
                    widget.addItems(field.options)
            case _:
                widget = QLineEdit()
        return widget

    def _load_values(self) -> None:
        """Load current config values into widgets."""
        for fields in TAB_DEFINITIONS.values():
            for field in fields:
                self._load_field_value(field)

    def _load_field_value(self, field: FieldDef) -> None:
        """Load a single field value from config."""
        widget = self._widgets[field.env_key]
        value = getattr(config, field.config_attr, None)

        # Handle SecretStr
        if hasattr(value, "get_secret_value"):
            value = value.get_secret_value() if value else ""

        match field.field_type:
            case FieldType.CHECKBOX:
                widget.setChecked(bool(value))
            case FieldType.COMBO:
                widget.setCurrentText(
                    str(value).upper() if field.env_key == "LOGGING_LEVEL" else str(value or "")
                )
            case _:
                widget.setText(str(value) if value is not None else "")

    def _get_widget_value(self, field: FieldDef) -> str:
        """Get the string value from a widget for saving."""
        widget = self._widgets[field.env_key]
        match field.field_type:
            case FieldType.CHECKBOX:
                return str(widget.isChecked())
            case FieldType.COMBO:
                return str(widget.currentText())
            case _:
                return str(widget.text())

    def _save_and_close(self) -> None:
        """Save settings to .env file and reload config."""
        new_values = {
            field.env_key: self._get_widget_value(field)
            for fields in TAB_DEFINITIONS.values()
            for field in fields
        }

        # Update environment variables
        os.environ.update(new_values)

        # Update .env file
        self._update_env_file(new_values)

        # Reload config
        try:
            reload_config()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reload config: {e}")

    @staticmethod
    def _update_env_file(new_values: dict[str, str]) -> None:
        """Update or create .env file with new values."""
        env_path = ".env"

        # Read existing lines
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Parse existing keys -> line index
        existing_keys = {
            line.split("=", 1)[0].strip(): i
            for i, line in enumerate(lines)
            if line.strip() and not line.startswith("#") and "=" in line
        }

        # Update or append
        for key, value in new_values.items():
            line_content = f"{key}={value}\n"
            if key in existing_keys:
                lines[existing_keys[key]] = line_content
            else:
                if lines and not lines[-1].endswith("\n"):
                    lines.append("\n")
                lines.append(line_content)
                existing_keys[key] = len(lines) - 1

        # Write back
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
