import re
from typing import Any, Dict, List

from src.core import settings
from src.database.connection import get_connection
from src.exceptions import (
    SqlMultiplosComandosException,
    SqlNaoPermitidoException,
    SqlVazioException,
)

COMANDOS_PERMITIDOS = ("SELECT", "WITH")

PALAVRAS_PROIBIDAS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "REPLACE", "TRUNCATE", "ATTACH", "DETACH", "PRAGMA", "VACUUM",
)

def limpar_sql(sql: str) -> str:
    limpo = sql.strip()
    limpo = re.sub(r"^```(?:sql)?", "", limpo, flags=re.IGNORECASE).strip()
    limpo = re.sub(r"```$", "", limpo).strip()
    return limpo

def validar_somente_select(sql: str) -> str:
    limpo = limpar_sql(sql)

    comandos = [c.strip() for c in limpo.rstrip(";").split(";") if c.strip()]
    if not comandos:
        raise SqlVazioException()
    if len(comandos) > 1:
        raise SqlMultiplosComandosException()

    primeira_palavra = comandos[0].split()[0].upper()
    if primeira_palavra not in COMANDOS_PERMITIDOS:
        raise SqlNaoPermitidoException(primeira_palavra)

    tokens = set(re.findall(r"[A-Za-z_]+", comandos[0].upper()))
    proibida = tokens.intersection(PALAVRAS_PROIBIDAS)
    if proibida:
        raise SqlNaoPermitidoException(sorted(proibida)[0])

    return comandos[0]

def aplicar_limite(sql: str) -> str:
    if re.search(r"\bLIMIT\b", sql, flags=re.IGNORECASE):
        return sql
    return f"{sql} LIMIT {settings.MAX_LINHAS}"

def executar_select(sql: str) -> Dict[str, Any]:
    valido = aplicar_limite(validar_somente_select(sql))

    with get_connection() as connection:
        cursor = connection.execute(valido)
        colunas: List[str] = [descricao[0] for descricao in cursor.description or []]
        linhas: List[Dict[str, Any]] = [dict(linha) for linha in cursor.fetchall()]

    return {"sql": valido, "colunas": colunas, "linhas": linhas}