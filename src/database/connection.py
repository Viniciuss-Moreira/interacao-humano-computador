import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional

from loguru import logger

from src.core import settings

_db_path: Optional[str] = None

def init_db(database_path: Optional[str] = None) -> None:
    global _db_path
    _db_path = str(database_path or settings.database_path)
    logger.info(f"Banco em uso: {_db_path}")

def get_db_path() -> str:
    return _db_path or str(settings.database_path)

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(get_db_path(), timeout=settings.TIMEOUT_SEGUNDOS)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()
        