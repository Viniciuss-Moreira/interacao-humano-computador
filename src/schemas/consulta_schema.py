from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

class ConsultaResponse(BaseModel):
    pergunta: str
    sql: str = Field(description="SQL que a LLM gerou, ja valido")
    colunas: List[str] = Field(default_factory=list)
    linhas: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)
    racicinio: Optional[str] = Field(
        default=None, description="Chain of Thought do modelo"
    )

class SqlResponse(BaseModel):
    sql: str
    colunas: List[str] = Field(default_factory=list)
    linhas: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)

class EsquemaResponse(BaseModel):
    ddl: str = Field(default="Esquema lido do proprio branco")

