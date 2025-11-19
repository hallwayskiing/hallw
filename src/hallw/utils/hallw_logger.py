import logging
from datetime import datetime
from pathlib import Path

from hallw.utils import config

log_dir = Path(config.logging_file_dir)
log_dir.mkdir(parents=True, exist_ok=True)

handlers: list[logging.Handler] = [
    logging.FileHandler(
        f"{config.logging_file_dir}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        encoding="utf-8",
    )
]


logging.basicConfig(
    level=getattr(logging, config.logging_level),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=handlers,
)

logging.getLogger("httpx").disabled = True
logging.getLogger("langchain_core.callbacks.manager").disabled = True
logger = logging.getLogger("hallw")
