from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError, OperationFailure, ExecutionTimeout, ConfigurationError
from bson.errors import InvalidId
from pydantic import ValidationError


class AppException(HTTPException):
    """Base para todas as exceções da aplicação."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class DatabaseConnectionException(AppException):
    def __init__(self, detail: str = "Database connection error"):
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail)


class DuplicateKeyException(AppException):
    def __init__(self, detail: str = "Duplicate key error"):
        super().__init__(status.HTTP_409_CONFLICT, detail)


class InvalidObjectIdException(AppException):
    def __init__(self, detail: str = "Invalid ObjectId format"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Document not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class DataValidationException(AppException):
    def __init__(self, detail: str = "Data validation error"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail)


class InvalidOperationException(AppException):
    def __init__(self, detail: str = "Invalid database operation"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class UpdateFailedException(AppException):
    def __init__(self, detail: str = "Update failed, no document modified"):
        super().__init__(status.HTTP_409_CONFLICT, detail)


class BusinessRuleViolation(AppException):
    def __init__(self, detail: str = "Business rule violation"):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


def translate_mongo_error(exc: Exception) -> AppException:
    if isinstance(exc, DuplicateKeyError):
        return DuplicateKeyException(str(exc))
    if isinstance(exc, InvalidId):
        return InvalidObjectIdException(str(exc))
    if isinstance(exc, ValidationError):
        return DataValidationException(str(exc))
    if isinstance(exc, ExecutionTimeout):
        return DatabaseConnectionException("Database operation timed out")
    if isinstance(exc, ConfigurationError):
        return DatabaseConnectionException("Database configuration/authentication error")
    if isinstance(exc, OperationFailure):
        return InvalidOperationException(str(exc))

    return AppException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(exc))
