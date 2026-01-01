from typing import Any
from datetime import datetime
from ninja import Schema

class ErrorSchema(Schema):
    statusCode: int
    message: str
    path: str
    timestamp: str

    @classmethod
    def from_exception(cls, status_code: int, path: str, message: str):
        """
        Método de conveniencia para crear un ErrorSchema desde una excepción
        """
        return cls(
            statusCode=status_code,
            timestamp=datetime.now().isoformat(),
            path=path,
            message=message
        )

class SuccessSchema(Schema):
    statusCode: int
    message: str
    path: str
    timestamp: str
    data: Any

    @classmethod
    def from_success(cls, status_code: int, path: str, message: str, data: Any):
        """
        Método de conveniencia para crear un SuccessSchema
        """
        return cls(
            statusCode=status_code,
            timestamp=datetime.now().isoformat(),
            path=path,
            message=message,
            data=data
        )