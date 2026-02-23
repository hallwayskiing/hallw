import logging
from datetime import datetime
from pathlib import Path

from hallw.utils import config

logger = logging.getLogger("hallw")


def init_logger(thread_id: str) -> None:
    """Initialize the HALLW logger configuration."""

    # If logger already has handlers, clear them
    if logger.hasHandlers():
        logger.handlers.clear()

    # Categorize logs by date
    log_dir = Path(config.logging_file_dir)
    now = datetime.now()
    timestamp = now.strftime("%H%M%S")
    date_str = now.strftime("%Y%m%d")

    day_log_dir = log_dir / date_str
    day_log_dir.mkdir(parents=True, exist_ok=True)

    short_id = str(thread_id)[:8]

    # Try to find existing log file for this thread_id in today's folder
    # Pattern: *_{short_id}.log
    existing_files = list(day_log_dir.glob(f"*_{short_id}.log"))

    if existing_files:
        # Sort by creation time (although likely only one) and pick the latest
        # actually picking the first match is probably fine if we assume 1 log per thread per day
        log_file_path = sorted(existing_files)[-1]
        mode = "a"
        is_appending = True
    else:
        log_file_path = day_log_dir / f"{timestamp}_{short_id}.log"
        mode = "w"
        is_appending = False

    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S")

    handlers = []

    file_handler = logging.FileHandler(log_file_path, mode=mode, encoding="utf-8")
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    log_level = getattr(logging, config.logging_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    for handler in handlers:
        logger.addHandler(handler)

    logging.getLogger("httpx").disabled = True
    logging.getLogger("langchain_core.callbacks.manager").disabled = True

    if is_appending:
        logger.info(f"{'=' * 20} RESUMING SESSION {'=' * 20}")
    else:
        logger.info(f"Thread ID: {thread_id}")
