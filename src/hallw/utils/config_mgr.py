from typing import List, Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =================================================
    # 1. Model Settings
    # =================================================
    model_name: str = "gemini/gemini-2.5-flash"
    openai_api_base: str = ""
    anthropic_api_base: str = ""
    model_temperature: float = 1
    model_max_output_tokens: int = 2560
    model_reasoning_effort: str = "low"  # low, medium, high
    model_reflection_threshold: int = 3
    model_max_recursion: int = 99
    model_recent_used: List[str] = []

    # =================================================
    # 2. Provider API Keys
    # =================================================
    openai_api_key: Optional[SecretStr] = None
    google_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    openrouter_api_key: Optional[SecretStr] = None
    nvidia_nim_api_key: Optional[SecretStr] = None
    deepseek_api_key: Optional[SecretStr] = None
    zai_api_key: Optional[SecretStr] = None
    moonshot_api_key: Optional[SecretStr] = None
    xiaomi_mimo_api_key: Optional[SecretStr] = None

    # =================================================
    # 3. LangSmith (Tracing)
    # =================================================
    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_api_key: Optional[SecretStr] = None
    langsmith_project: str = "HALLW"

    # =================================================
    # 4. Logging
    # =================================================
    logging_level: str = "INFO"
    logging_file_dir: str = "logs"
    logging_max_chars: int = 200

    # =================================================
    # 5. Exec & Search
    # =================================================
    auto_allow_exec: bool = False
    auto_allow_blacklist: List[str] = []
    search_engine: str = "brave"  # "brave" or "bocha"
    search_result_count: int = 5
    brave_search_api_key: Optional[SecretStr] = None
    bocha_api_key: Optional[SecretStr] = None

    # =================================================
    # 6. Playwright & Browser
    # =================================================
    chrome_user_data_dir: Optional[str] = None
    # Playwright timeouts (in milliseconds)
    pw_goto_timeout: int = 10000
    pw_click_timeout: int = 6000
    pw_cdp_timeout: int = 1000

    # =================================================
    # Pydantic config
    # =================================================
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)


# Export
config = Settings()


def save_config_to_env(updates: dict):
    """
    Updates the .env file with new values and reloads the config.
    Preserves comments and structure of the existing .env file if possible,
    or just appends/overwrites.
    Simple implementation: Read .env lines, replace matching keys, write back.
    """
    import json
    import os

    def format_env_value(val):
        """Format a value for .env file. Lists are JSON-encoded with double quotes."""
        if isinstance(val, list):
            return json.dumps(val)  # Returns ["item1", "item2"] format
        elif isinstance(val, bool):
            return str(val)
        return val

    env_path = ".env"

    if not os.path.exists(env_path):
        # Create new
        with open(env_path, "w", encoding="utf-8") as f:
            for k, v in updates.items():
                f.write(f"{k.upper()}={format_env_value(v)}\n")
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
                    new_lines.append(f"{key}={format_env_value(val)}\n")
                    updated_keys.add(key.lower())
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Append new keys that weren't in the file
        for k, v in updates.items():
            if k.lower() not in updated_keys:
                new_lines.append(f"{k.upper()}={format_env_value(v)}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    # Reload config from .env with proper type conversion
    from dotenv import load_dotenv

    global config
    load_dotenv(override=True)
    new_config = Settings()
    # Update existing object's attributes (preserves references in other modules)
    for key, value in new_config.model_dump().items():
        setattr(config, key, value)
