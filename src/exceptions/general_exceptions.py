from src.strings import (
    ERROR_INTERNAL_SERVER,
    ERROR_INVALID_INPUT,
    ERROR_INVALID_REQUEST,
    ERROR_RESOURCE_NOT_FOUND,
)

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundException(AppException):
    def __init__(self, message: str = ERROR_RESOURCE_NOT_FOUND):
        super().__init__(message, status_code=404)

class BadRequestException(AppException):
    def __init__(self, message: str = ERROR_INVALID_REQUEST):
        super().__init__(message, status_code=400)

class InternalServerException(AppException):
    def __init__(self, message: str = ERROR_INTERNAL_SERVER):
        super().__init__(message, status_code=500)

class UnprocessableEntity(AppException):
    def __init__(self, message: str = ERROR_INVALID_INPUT):
        super().__init__(message, status_code=422)

class ServiceUnavailableException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=503)
        
        