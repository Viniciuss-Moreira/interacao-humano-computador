from src.strings import (
    ERROR_INVALID_INPUT,
    ERROR_INVALID_REQUEST,
    ERROR_LLM_INDISPONIVEL,
    ERROR_SQL_INVALIDO,
    ERROR_SQL_MULTIPLOS_COMANDOS,
    ERROR_SQL_NAO_PERMITIDO,
    ERROR_SQL_VAZIO,
    ERROR_TRANSCRICAO,
)

from .general_exceptions import(
    BadRequestException,
    ServiceUnavailableException,
    UnprocessableEntity,
)

class SqlNaoPermitidoException(BadRequestException):

    def __init__(self, comando: str):
        super().__init__(ERROR_SQL_NAO_PERMITIDO.format(comando=comando))


class SqlMultiplosComandosException(BadRequestException):
    def __init__(self):
        super().__init__(ERROR_SQL_MULTIPLOS_COMANDOS)

class SqlVazioException(BadRequestException):
    def __init__(self):
        super().__init__(ERROR_SQL_VAZIO)

class SqlInvalidoException(UnprocessableEntity):
    """Para quando a LLM gerar um SQL quebrado"""
    def __init__(self, erro: str):
        super().__init__(ERROR_SQL_INVALIDO.format(erro=erro))

class LlmIndisponivelException(ServiceUnavailableException):
    def __init__(self, erro: str):
        super().__init__(ERROR_LLM_INDISPONIVEL.format(erro=erro))

class TranscricaoException(UnprocessableEntity):
    def __init__(self, erro: str):
        super().__init__(ERROR_TRANSCRICAO.format(erro=erro))

