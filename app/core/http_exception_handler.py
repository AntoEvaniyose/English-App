from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


async def custom_http_exception_handler(
    request: Request,
    exc: HTTPException
):
    status_map = {
        400: "Failed 'Bad Request'",
        401: "Failed 'Unauthorized'",
        403: "Failed 'Forbidden'",
        404: "Failed 'Not Found'",
        422: "Failed 'Unprocessable Entity'",
        500: "Failed 'Internal Server Error'",
    }

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": status_map.get(exc.status_code, "Failed"),
            "status_code": exc.status_code,
            "errors": exc.detail,
        },
    )