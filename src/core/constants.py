import os 
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
SOURCE_FOLDER = os.path.join(BASE_DIR, "src")

LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "estoque_api.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()

