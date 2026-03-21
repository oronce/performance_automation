"""
logger.py
─────────
Central logging setup for cache_builder.

Usage in any module:
    from logger import get_logger
    logger = get_logger()

    logger.info("something happened")
    logger.error("something failed", exc_info=True)   # includes full traceback

Log file: assets/logs/cache_builder.log
  - Rotates at 5 MB, keeps 5 backups
  - Always appends (safe to run multiple times)
"""

import logging
import os
from logging.handlers import RotatingFileHandler

_HERE    = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(_HERE, "assets", "logs", "cache_builder.log")
_FMT     = "%(asctime)s [%(levelname)-8s] %(message)s"
_DATE    = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str = "cache_builder") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger   # already configured — avoid duplicate handlers

    logger.setLevel(logging.DEBUG)

    # make sure the logs directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # file handler — rotate at 5 MB, keep last 5 files
    fh = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(_FMT, datefmt=_DATE))

    logger.addHandler(fh)
    return logger