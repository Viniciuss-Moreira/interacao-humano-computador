from functools import lru_cache

import dspy
from loguru import logger

from src.agent.signatures import TextToSQL
from src.core import settings


def configure_llm() -> None:
    """Aponta o DSPy para o servidor local do modelo"""
    lm = dspy.LM(
        settings.LLM_MODEL,
        api_base=settings.LLM_API_BASE,
        api_key=settings.LLM_API_KEY,
    )
    dspy.configure(lm=lm)
    logger.info(f"LLM configurada: {settings.LLM_MODEL} em {settings.LLM_API_BASE}")


class ReliableSQLGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_sql = dspy.ChainOfThought(TextToSQL)

    def forward(self, dbschema: str, question: str):
        # os nomes tem que bater com os InputField da TextToSQL.
        return self.generate_sql(dbschema=dbschema, question=question)


@lru_cache
def get_generator() -> ReliableSQLGenerator:
    """uma instancia so: montar o modulo DSPy a cada pergunta e desperdicio."""
    return ReliableSQLGenerator()
