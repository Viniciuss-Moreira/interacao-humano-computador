"""
Pacote models — módulos de IA desacoplados.

Módulos:
  - llama_server   → infra do llama.cpp
  - qwen3_model    → geração de SQL via Qwen3 / DSPy
  - whisper_model  → transcrição de áudio via Whisper
"""

from .llama_server import (
    download_model,
    start_llama_server,
    stop_llama_server,
    LLAMA_API_BASE,
)

from .qwen3_model import (
    init_ia,
    generate_sql,
)

from .whisper_model import whisper_transcribe
