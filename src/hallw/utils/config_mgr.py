from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =================================================
    # 1. Model Settings (LLM)
    # =================================================
    model_name: str = "gemini-2.5-flash-lite"  # Recommended: fast and free in Google AI Studio
    model_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    model_api_key: SecretStr
    model_temperature: float = 0.25
    model_max_output_tokens: int = 4096
    model_reflection_threshold: int = 3
    model_max_recursion: int = 50

    # =================================================
    # 2. LangSmith (Tracing)
    # =================================================
    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: Optional[SecretStr] = None
    langsmith_project: str = "HALLW"

    # =================================================
    # 3. Logging
    # =================================================``
    logging_level: str = "INFO"
    logging_file_dir: str = "logs"
    max_message_chars: int = 50

    # =================================================
    # 4. Playwright & Browser
    # =================================================
    prefer_local_chrome: bool = True
    chrome_user_data_dir: Optional[str] = None
    cdp_port: int = 9222
    pw_headless_mode: bool = False
    pw_window_width: int = 1920
    pw_window_height: int = 1080
    keep_browser_open: bool = True
    browser_search_engine: str = "google"
    search_result_count: int = 10
    max_page_content_chars: int = 2000
    # Timeouts (in milliseconds)
    manual_captcha_timeout: int = 60000
    pw_goto_timeout: int = 10000
    pw_click_timeout: int = 6000
    pw_cdp_timeout: int = 1000

    # =================================================
    # 5. File Operations
    # =================================================
    file_read_dir: str = "."
    file_save_dir: str = "workspace/"
    file_max_read_chars: int = 5000

    # =================================================
    # Pydantic config
    # =================================================
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )


# Export
config = Settings()


def reload_config():
    global config
    new_config = Settings()
    for key, value in new_config.model_dump().items():
        setattr(config, key, value)
