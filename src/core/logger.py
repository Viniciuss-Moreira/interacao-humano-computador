import os
import sys

from loguru import logger

from .constants import LOG_DIR,LOG_FILE, LOG_LEVEL

def configure_logger():
    """Configure logger with proper paths for both dev and frozen executable."""
    os.makedirs(LOG_DIR, exist_ok=True)
    logger.remove()
    logger.add(lambda m: sys.stderr.write(m), level=LOG_LEVEL)
    logger.add(LOG_FILE, level="DEBUG", rotation="10 MB", retention="30 days")