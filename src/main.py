from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.agent import configure_llm
from src.core import configure_logger, settings
from src.database import create_db, get_db_path, init_db
from src.exceptions import AppException
from src.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logger()
    init_db()
    create_db()
    configure_llm()
    yield



app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/saude", tags=["geral"])
def saude():
    return {"status": "ok", "banco": get_db_path(), "modelo": settings.LLM_MODEL}