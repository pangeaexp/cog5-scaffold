# src/logger.py
import logging
import logging.handlers
import json
import os
from typing import Optional

LOG_DIR = os.getenv("COG5_LOG_DIR", "./log/cog5")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, os.getenv("COG5_LOG_FILE", "cog5.log"))

def configure_logging(level: str = "INFO"):
    lvl = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=lvl, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

def _format_json(record: logging.LogRecord) -> str:
    payload = {
        "ts": record.created,
        "level": record.levelname,
        "name": record.name,
        "msg": record.getMessage(),
        "module": record.module,
        "func": record.funcName,
        "lineno": record.lineno,
    }
    if record.exc_info:
        payload["exc"] = True
    return json.dumps(payload, default=str)

def get_logger(name: str = "cog5", *, json_format: Optional[bool]=None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    level = os.getenv("COG5_LOG_LEVEL", "INFO").upper()
    logger.setLevel(level)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    if json_format is None:
        json_format = os.getenv("COG5_LOG_JSON", "false").lower() == "true"
    if json_format:
        # Simple JSON formatting: replace record.msg with JSON string
        def format_filter(record):
            record.msg = _format_json(record)
            return True
        ch.addFilter(format_filter)
        ch.setFormatter(logging.Formatter("%(message)s"))
    else:
        ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    # Rotating file handler
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=int(os.getenv("COG5_LOG_MAX_BYTES", 10_000_000)),
        backupCount=int(os.getenv("COG5_LOG_BACKUP", 5)),
    )
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s [%(module)s:%(lineno)d]: %(message)s"))

    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = False
    return logger