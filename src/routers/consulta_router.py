from typing import Annotated

from fastapi import APIRouter, Query, status

from src.database import get_schema_ddl
from src.schemas import ConsultaResponse, EsquemaResponse, SqlResponse
from src.services import consulta_service

router = APIRouter(prefix="/consulta", tags=["consulta"])


@router.get("", response_model=ConsultaResponse, status_code=status.HTTP_200_OK)
def consultar(
    pergunta: Annotated[
        str,
        Query(
            min_length=3,
            max_length=300,
            description="Pergunta em portugues sobre o estoque",
            examples=["Quais produtos vencem hoje?"],
        ),
    ],
) -> ConsultaResponse:
    """Rota principal: pergunta em linguagem natural -> SQL -> resultado."""
    return consulta_service.consultar(pergunta)


@router.get("/sql", response_model=SqlResponse)
def executar_sql(
    sql: Annotated[str, Query(min_length=6, max_length=2000)],
) -> SqlResponse:
    """Executa um SELECT direto, sem passar pela LLM.

    Serve para testar o banco e para comparar o SQL da LLM com o SQL
    escrito a mao 
    """
    return consulta_service.executar(sql)


@router.get("/esquema", response_model=EsquemaResponse)
def esquema() -> EsquemaResponse:
    """Esquema lido do proprio banco, igual ao que vai no prompt."""
    return EsquemaResponse(ddl=get_schema_ddl())