from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.db.engine import close_database

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    close_database()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Advanced-database wildlife monitoring API.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "request_validation_failed",
                "message": "The request did not match the expected format.",
                "details": {"issues": exc.errors()},
                "request_id": request.state.request_id,
            }
        },
    )


@app.get("/health", tags=["system"], include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(v1_router)
