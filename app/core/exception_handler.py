from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from fastapi import Request


# =========================
# FASTAPI VALIDATION
# =========================
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):

    error = exc.errors()[0]

    return JSONResponse(
        status_code=422,
        content={
            "status": "Failed 'Validation Error'",
            "status_code": 422,
            "errors": error["msg"]
        }
    )


# =========================
# PYDANTIC VALIDATION
# =========================
async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError
):

    error = exc.errors()[0]

    return JSONResponse(
        status_code=422,
        content={
            "status": "Failed 'Validation Error'",
            "status_code": 422,
            "errors": error["msg"].replace("Value error, ", "")
        }
    )