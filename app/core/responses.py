from fastapi.responses import JSONResponse
from typing import Any, List, Optional
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from fastapi.exceptions import RequestValidationError

 
class CustomResponse:
    @staticmethod
    def success(message: str, data: Optional[Any] = None) -> JSONResponse:
        if isinstance(data, list):
            data = [item.model_dump() if hasattr(item, 'model_dump') else item for item in data]
        elif hasattr(data, 'model_dump'):
            data = data.model_dump()
 
        return JSONResponse(
            status_code=200,
            content={
                "status": "Success",
                "status_code": 200,
                "message": message,
                "data": jsonable_encoder(data) if data is not None else {},
            }
        )
 
    @staticmethod
    def not_found(message: str) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "status": "Failed 'Not Found'",
                "status_code": 404,
                "errors": message,
            }
        )
 
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "status": "Failed 'Unauthorized'",
                "status_code": 401,
                "errors": message,
            }
        )
 
    @staticmethod
    def bad_request(message: str = "Bad Request") -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "status": "Failed 'Bad Request'",
                "status_code": 400,
                "errors": message,
            }
        )
 
    @staticmethod
    def forbidden(message: str = "Forbidden") -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "status": "Failed 'Forbidden'",
                "status_code": 403,
                "errors": message,
            }
        )
 
    @staticmethod
    def unprocessable_entity(message: str = "Unprocessable Entity") -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "status": "Failed 'Unprocessable Entity'",
                "status_code": 422,
                "errors": message,
            }
        )
 
    @staticmethod
    def server_error(message: str) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "status": "Failed 'Internal Server Error'",
                "status_code": 500,
                "errors": message,
            }
        )
    
   