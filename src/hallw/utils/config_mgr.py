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
    # Timeouts (in seconds)
    manual_captcha_timeout: int = 60
    # Playwright timeouts (in milliseconds)
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
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)


# Export
config = Settings()


def reload_config():
    global config
    new_config = Settings()
    for key, value in new_config.model_dump().items():
        setattr(config, key, value)


def save_config_to_env(updates: dict):
    """
    Updates the .env file with new values and reloads the config.
    Preserves comments and structure of the existing .env file if possible,
    or just appends/overwrites.
    Simple implementation: Read .env lines, replace matching keys, write back.
    """
    import os

    env_path = ".env"

    if not os.path.exists(env_path):
        # Create new
        with open(env_path, "w", encoding="utf-8") as f:
            for k, v in updates.items():
                f.write(f"{k.upper()}={v}\n")
    else:
        # Read existing
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        updated_keys = set()

        for line in lines:
            line_strip = line.strip()
            if not line_strip or line_strip.startswith("#"):
                new_lines.append(line)
                continue

            # Simple parsing of KEY=VALUE
            if "=" in line:
                key = line.split("=", 1)[0].strip()
                if key.lower() in updates:
                    # Update line
                    val = updates[key.lower()]
                    new_lines.append(f"{key}={val}\n")
                    updated_keys.add(key.lower())
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Append new keys that weren't in the file
        for k, v in updates.items():
            if k.lower() not in updated_keys:
                new_lines.append(f"{k.upper()}={v}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    # Force reload logic in-memory
    # However, since we are using global 'config', we can just update attributes
    # But for type safety/validation, creating a new Settings() (which reads .env) is safer
    # IF pydantic reads .env on instantiation.
    reload_config()
