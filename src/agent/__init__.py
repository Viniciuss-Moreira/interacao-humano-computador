from .generator import (
    RecursiveSQLGenerator,
    TextToSQL,
    RefineSQL,
    get_db_schema,
    init_ia,
    generate_sql,
)
from .llama_server import download_model, start_llama_server, stop_llama_server
from .transcriber import transcrever, whisper_transcribe

# Aliases para compatibilidade com o restante de src/
configure_llm = init_ia
get_generator = RecursiveSQLGenerator

__all__ = [
    "TextToSQL",
    "RefineSQL",
    "RecursiveSQLGenerator",
    "configure_llm",
    "get_generator",
    "get_db_schema",
    "init_ia",
    "generate_sql",
    "download_model",
    "start_llama_server",
    "stop_llama_server",
    "transcrever",
    "whisper_transcribe",
]
