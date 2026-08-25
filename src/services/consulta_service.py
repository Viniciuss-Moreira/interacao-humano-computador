"""orquestração: pergunta -> SQL -> validacao -> execucao -> resposta."""

import sqlite3

from loguru import logger

from src.agent import get_generator, transcrever
from src.database import executar_select, get_schema_ddl
from src.exceptions import (
    AppException,
    LlmIndisponivelException,
    SqlInvalidoException,
)
from src.schemas import ConsultaResponse, SqlResponse
from src.strings import SUCCESS_CONSULTA, SUCCESS_SQL_GERADO

class ConsultaService:

    def gerar_sql(self, pergunta: str) -> tuple:
        try: 
            predicao = get_generator().forward(
                dbschema=get_schema_ddl(), question=pergunta
            )
        except Exception as erro:
            logger.error(f"Falha ao gerar SQL: {erro}")
            raise LlmIndisponivelException(str(erro)) from erro

        sql = predicao.sql_query
        raciocinio = getattr(predicao, "reasoning", None)
        logger.info(SUCCESS_SQL_GERADO.format(pergunta=pergunta, sql=sql)) 
        return sql, raciocinio

    def consultar(self, pergunta: str) -> ConsultaResponse:
        sql, raciocinio = self.gerar_sql(pergunta)
        resultado = self.executar(sql)
        return ConsultaResponse(
            pergunta=pergunta,
            sql=resultado.sql,
            colunas=resultado.colunas,
            linhas=resultado.linhas,
            total=resultado.total,
            raciocinio=raciocinio,
        )

    def consultar_audio(self, filepath: str) -> ConsultaResponse:
        return self.consultar(transcrever(filepath))

    def executar(self, sql: str) -> SqlResponse:
        try:
            resultado = executar_select(sql)
        except AppException:
            raise
        except sqlite3.Error as erro:
            logger.error(f"SQL invalido: {erro}")
            raise SqlInvalidoException(str(erro)) from erro

        logger.info(SUCCESS_CONSULTA.format(total=len(resultado["linhas"])))
        return SqlResponse(
            sql=resultado["sql"],
            colunas=resultado["colunas"],
            linhas=resultado["linhas"],
            total=len(resultado["linhas"]),
        )


consulta_service = ConsultaService()

        