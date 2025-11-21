import logging
from datetime import datetime
from pathlib import Path

from hallw.utils import config

# Create logs directory
log_dir = Path(config.logging_file_dir)
log_dir.mkdir(parents=True, exist_ok=True)

# Configure hallw logger with its own handler to avoid affecting global logging
logger = logging.getLogger("hallw")
logger.setLevel(getattr(logging, config.logging_level))
logger.propagate = False  # Don't propagate to root logger

# Create file handler with formatter
file_handler = logging.FileHandler(
    f"{config.logging_file_dir}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    encoding="utf-8",
)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
