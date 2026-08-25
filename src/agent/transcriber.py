from functools import lru_cache

import whisper
from loguru import logger

from src.core import settings
from src.exceptions import TranscricaoException
from src.strings import SUCCESS_TRANSCRICAO

@lru_cache
def _load_model(nome: str):
    """carrega e guarda o modelo whisper em memoria"""
    logger.info(f"Carregando modelo Whisper '{nome}'...")
    return whisper.load_model(nome)

def transcrever(filepath: str) -> str:
    """transcreve um audio para textp"""

    try:
        modelo = _load_model(settings.WHISPER_MODEL)
        resultado = modelo.transcribe(filepath)
    except Exception as erro: 
        raise TranscricaoException(str(erro)) from erro

    texto = resultado["text"].strip()
    logger.info(SUCCESS_TRANSCRICAO.format(texto=texto))
    return texto
