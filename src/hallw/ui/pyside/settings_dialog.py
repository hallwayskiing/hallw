import os

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


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(700, 800)

        self.setStyleSheet(SETTINGS_STYLE)

        self._init_ui()
        self._load_current_values()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Tabs for different categories
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # =================================================
        # 1. Model Settings
        # =================================================
        self.tab_model = QWidget()
        self.tab_model.setObjectName("TabContent")
        self.form_model = QFormLayout(self.tab_model)
        self.tabs.addTab(self.tab_model, "Model")

        self.inp_model_name = QLineEdit()
        self.inp_model_endpoint = QLineEdit()
        self.inp_model_api_key = QLineEdit()
        self.inp_model_api_key.setEchoMode(QLineEdit.Password)
        self.inp_model_temp = QLineEdit()
        self.inp_model_max_tokens = QLineEdit()
        self.inp_model_reflection_threshold = QLineEdit()

        self.form_model.addRow("Model Name:", self.inp_model_name)
        self.form_model.addRow("Endpoint:", self.inp_model_endpoint)
        self.form_model.addRow("API Key:", self.inp_model_api_key)
        self.form_model.addRow("Temperature:", self.inp_model_temp)
        self.form_model.addRow("Max Output Tokens:", self.inp_model_max_tokens)
        self.form_model.addRow("Reflection Threshold:", self.inp_model_reflection_threshold)

        # =================================================
        # 2. LangSmith
        # =================================================
        self.tab_langsmith = QWidget()
        self.tab_langsmith.setObjectName("TabContent")
        self.form_langsmith = QFormLayout(self.tab_langsmith)
        self.tabs.addTab(self.tab_langsmith, "LangSmith")

        self.chk_ls_tracing = QCheckBox()
        self.inp_ls_endpoint = QLineEdit()
        self.inp_ls_api_key = QLineEdit()
        self.inp_ls_api_key.setEchoMode(QLineEdit.Password)
        self.inp_ls_project = QLineEdit()

        self.form_langsmith.addRow("Enable Tracing:", self.chk_ls_tracing)
        self.form_langsmith.addRow("Endpoint:", self.inp_ls_endpoint)
        self.form_langsmith.addRow("API Key:", self.inp_ls_api_key)
        self.form_langsmith.addRow("Project:", self.inp_ls_project)

        # =================================================
        # 3. Logging
        # =================================================
        self.tab_logging = QWidget()
        self.tab_logging.setObjectName("TabContent")
        self.form_logging = QFormLayout(self.tab_logging)
        self.tabs.addTab(self.tab_logging, "Logging")

        self.inp_logging_level = QComboBox()
        self.inp_logging_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

        self.inp_logging_dir = QLineEdit()
        self.inp_max_msg_chars = QLineEdit()

        self.form_logging.addRow("Logging Level:", self.inp_logging_level)
        self.form_logging.addRow("Log Directory:", self.inp_logging_dir)
        self.form_logging.addRow("Max Message Chars:", self.inp_max_msg_chars)

        # =================================================
        # 4. Browser / Playwright
        # =================================================
        self.tab_browser = QWidget()
        self.tab_browser.setObjectName("TabContent")
        scroll_browser = QScrollArea()
        scroll_browser.setWidgetResizable(True)
        scroll_browser.setWidget(self.tab_browser)
        self.form_browser = QFormLayout(self.tab_browser)
        self.tabs.addTab(scroll_browser, "Browser")

        self.chk_prefer_local = QCheckBox()
        self.inp_chrome_user_data = QLineEdit()
        self.inp_cdp_port = QLineEdit()
        self.chk_headless = QCheckBox()
        self.inp_pw_width = QLineEdit()
        self.inp_pw_height = QLineEdit()
        self.chk_keep_open = QCheckBox()

        self.inp_search_engine = QComboBox()
        self.inp_search_engine.addItems(["Google", "Bing", "Baidu"])

        self.inp_search_count = QLineEdit()
        self.inp_max_page_chars = QLineEdit()

        self.inp_captcha_timeout = QLineEdit()
        self.inp_goto_timeout = QLineEdit()
        self.inp_click_timeout = QLineEdit()
        self.inp_cdp_timeout = QLineEdit()

        self.form_browser.addRow("Prefer Local Chrome:", self.chk_prefer_local)
        self.form_browser.addRow("Chrome User Data Dir:", self.inp_chrome_user_data)
        self.form_browser.addRow("CDP Port:", self.inp_cdp_port)
        self.form_browser.addRow("Headless Mode:", self.chk_headless)
        self.form_browser.addRow("Window Width:", self.inp_pw_width)
        self.form_browser.addRow("Window Height:", self.inp_pw_height)
        self.form_browser.addRow("Keep Page Open:", self.chk_keep_open)
        self.form_browser.addRow("Search Engine:", self.inp_search_engine)
        self.form_browser.addRow("Search Result Count:", self.inp_search_count)
        self.form_browser.addRow("Max Page Content Chars:", self.inp_max_page_chars)

        self.form_browser.addRow("Manual Captcha Timeout (ms):", self.inp_captcha_timeout)
        self.form_browser.addRow("Goto Timeout (ms):", self.inp_goto_timeout)
        self.form_browser.addRow("Click Timeout (ms):", self.inp_click_timeout)
        self.form_browser.addRow("CDP Timeout (ms):", self.inp_cdp_timeout)

        # =================================================
        # 5. File Operations
        # =================================================
        self.tab_file = QWidget()
        self.tab_file.setObjectName("TabContent")
        self.form_file = QFormLayout(self.tab_file)
        self.tabs.addTab(self.tab_file, "File Ops")

        self.inp_file_read_dir = QLineEdit()
        self.inp_file_save_dir = QLineEdit()
        self.inp_file_max_read = QLineEdit()

        self.form_file.addRow("Read Directory:", self.inp_file_read_dir)
        self.form_file.addRow("Save Directory:", self.inp_file_save_dir)
        self.form_file.addRow("Max Read Chars:", self.inp_file_max_read)

        # =================================================
        # 6. Interactive
        # =================================================
        self.tab_interactive = QWidget()
        self.tab_interactive.setObjectName("TabContent")
        self.form_interactive = QFormLayout(self.tab_interactive)
        self.tabs.addTab(self.tab_interactive, "Interactive")

        self.chk_allow_ask = QCheckBox()

        self.form_interactive.addRow("Allow Ask Info Tool:", self.chk_allow_ask)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._save_and_close)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _load_current_values(self):
        # Model
        self.inp_model_name.setText(config.model_name)
        self.inp_model_endpoint.setText(config.model_endpoint)
        if config.model_api_key:
            self.inp_model_api_key.setText(config.model_api_key.get_secret_value())
        self.inp_model_temp.setText(str(config.model_temperature))
        self.inp_model_max_tokens.setText(str(config.model_max_output_tokens))
        self.inp_model_reflection_threshold.setText(str(config.model_reflection_threshold))

        # LangSmith
        self.chk_ls_tracing.setChecked(config.langsmith_tracing)
        self.inp_ls_endpoint.setText(config.langsmith_endpoint)
        if config.langsmith_api_key:
            self.inp_ls_api_key.setText(config.langsmith_api_key.get_secret_value())
        self.inp_ls_project.setText(config.langsmith_project)

        # Logging
        self.inp_logging_level.setCurrentText(config.logging_level.upper())
        self.inp_logging_dir.setText(config.logging_file_dir)
        self.inp_max_msg_chars.setText(str(config.max_message_chars))

        # Browser
        self.chk_prefer_local.setChecked(config.prefer_local_chrome)
        self.inp_chrome_user_data.setText(config.chrome_user_data_dir or "")
        self.inp_cdp_port.setText(str(config.cdp_port))
        self.chk_headless.setChecked(config.pw_headless_mode)
        self.inp_pw_width.setText(str(config.pw_window_width))
        self.inp_pw_height.setText(str(config.pw_window_height))
        self.chk_keep_open.setChecked(config.keep_page_open)

        self.inp_search_engine.setCurrentText(config.browser_search_engine)

        self.inp_search_count.setText(str(config.search_result_count))
        self.inp_max_page_chars.setText(str(config.max_page_content_chars))

        self.inp_captcha_timeout.setText(str(config.manual_captcha_timeout))
        self.inp_goto_timeout.setText(str(config.pw_goto_timeout))
        self.inp_click_timeout.setText(str(config.pw_click_timeout))
        self.inp_cdp_timeout.setText(str(config.pw_cdp_timeout))

        # File
        self.inp_file_read_dir.setText(config.file_read_dir)
        self.inp_file_save_dir.setText(config.file_save_dir)
        self.inp_file_max_read.setText(str(config.file_max_read_chars))

        # Interactive
        self.chk_allow_ask.setChecked(config.allow_ask_info_tool)

    def _save_and_close(self):
        # Collect values
        new_values = {
            "MODEL_NAME": self.inp_model_name.text(),
            "MODEL_ENDPOINT": self.inp_model_endpoint.text(),
            "MODEL_API_KEY": self.inp_model_api_key.text(),
            "MODEL_TEMPERATURE": self.inp_model_temp.text(),
            "MODEL_MAX_OUTPUT_TOKENS": self.inp_model_max_tokens.text(),
            "MODEL_REFLECTION_THRESHOLD": self.inp_model_reflection_threshold.text(),
            "LANGSMITH_TRACING": str(self.chk_ls_tracing.isChecked()),
            "LANGSMITH_ENDPOINT": self.inp_ls_endpoint.text(),
            "LANGSMITH_API_KEY": self.inp_ls_api_key.text(),
            "LANGSMITH_PROJECT": self.inp_ls_project.text(),
            "LOGGING_LEVEL": self.inp_logging_level.currentText(),
            "LOGGING_FILE_DIR": self.inp_logging_dir.text(),
            "MAX_MESSAGE_CHARS": self.inp_max_msg_chars.text(),
            "PREFER_LOCAL_CHROME": str(self.chk_prefer_local.isChecked()),
            "CHROME_USER_DATA_DIR": self.inp_chrome_user_data.text(),
            "CDP_PORT": self.inp_cdp_port.text(),
            "PW_HEADLESS_MODE": str(self.chk_headless.isChecked()),
            "PW_WINDOW_WIDTH": self.inp_pw_width.text(),
            "PW_WINDOW_HEIGHT": self.inp_pw_height.text(),
            "KEEP_PAGE_OPEN": str(self.chk_keep_open.isChecked()),
            "BROWSER_SEARCH_ENGINE": self.inp_search_engine.currentText(),
            "SEARCH_RESULT_COUNT": self.inp_search_count.text(),
            "MAX_PAGE_CONTENT_CHARS": self.inp_max_page_chars.text(),
            "MANUAL_CAPTCHA_TIMEOUT": self.inp_captcha_timeout.text(),
            "PW_GOTO_TIMEOUT": self.inp_goto_timeout.text(),
            "PW_CLICK_TIMEOUT": self.inp_click_timeout.text(),
            "PW_CDP_TIMEOUT": self.inp_cdp_timeout.text(),
            "FILE_READ_DIR": self.inp_file_read_dir.text(),
            "FILE_SAVE_DIR": self.inp_file_save_dir.text(),
            "FILE_MAX_READ_CHARS": self.inp_file_max_read.text(),
            "ALLOW_ASK_INFO_TOOL": str(self.chk_allow_ask.isChecked()),
        }

        # Update os.environ to ensure pydantic picks up changes immediately
        for k, v in new_values.items():
            os.environ[k] = v

        # Update .env file
        self._update_env_file(new_values)

        # Reload config
        try:
            reload_config()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reload config: {e}")

    def _update_env_file(self, new_values: dict[str, str]):
        env_path = ".env"

        # Read existing lines
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        # Parse existing keys
        existing_keys = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key = line.split("=", 1)[0].strip()
                existing_keys[key] = i

        # Update or Append
        for key, value in new_values.items():
            line_content = f"{key}={value}\n"

            if key in existing_keys:
                lines[existing_keys[key]] = line_content
            else:
                # If not found, append to the end
                if lines and not lines[-1].endswith("\n"):
                    lines.append("\n")
                lines.append(line_content)
                # Update index for future reference in this loop
                existing_keys[key] = len(lines) - 1

        # Write back
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
