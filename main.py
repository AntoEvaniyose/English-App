from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pathlib import Path
from contextlib import asynccontextmanager  # ← add this
import os
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handler import (
    validation_exception_handler,
    pydantic_validation_exception_handler
)
from app.core.http_exception_handler import custom_http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.db.base import Base
from app.db.session import engine
from app.mcp.server import mcp

# =========================
# MCP App (must be before FastAPI init)
# =========================
mcp_app = mcp.http_app(transport="streamable-http")  # ← move up here

# =========================
# Lifespan (3 lines, nothing more)
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_app.lifespan(mcp_app):
        yield

# =========================
# FastAPI App
# =========================
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan  # ← only change to FastAPI() call
)

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent

# =========================
# Static Files
# =========================
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

app.mount("/", mcp_app)  # exposes /mcp

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "FastAPI English App is running"}

# # =========================
# # STATUS LABEL MAP
# # =========================
# STATUS_MAP = {
#     400: "Bad Request",
#     401: "Unauthorized",
#     403: "Forbidden",
#     404: "Not Found",
#     422: "Unprocessable Entity",
#     500: "Internal Server Error"
# }

# # =========================
# # HTTPException Handler
# # =========================
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     label = STATUS_MAP.get(exc.status_code, "Error")

#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "status": f"Failed '{label}'",
#             "status_code": exc.status_code,
#             "errors": exc.detail,
#         },
#     )


# # =========================
# # Validation Error Handler (422)
# # =========================
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=422,
#         content={
#             "status": "Failed 'Unprocessable Entity'",
#             "status_code": 422,
#             "errors": exc.errors(),
#         },
#     )
