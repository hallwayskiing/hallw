import logging
from datetime import datetime
from pathlib import Path

from hallw.utils import config

logger = logging.getLogger("hallw")


def init_logger(task_id: str) -> None:
    """Initialize the HALLW logger configuration."""

    # If logger already has handlers, do not re-initialize
    if logger.hasHandlers():
        return

    # Categorize logs by date
    log_dir = Path(config.logging_file_dir)
    now = datetime.now()
    timestamp = now.strftime("%H%M%S")
    date_str = now.strftime("%Y%m%d")

    day_log_dir = log_dir / date_str
    day_log_dir.mkdir(parents=True, exist_ok=True)

    short_id = str(task_id)[:8]
    log_file_path = day_log_dir / f"{timestamp}_{short_id}.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S"
    )

    handlers = []

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    log_level = getattr(logging, config.logging_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    for handler in handlers:
        logger.addHandler(handler)

    logging.getLogger("httpx").disabled = True
    logging.getLogger("langchain_core.callbacks.manager").disabled = True
