from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.api.v1.router import api_router
from app.core.middleware import setup_middleware
from app.core.logging import setup_logging
from app.core.exceptions import StockPulseException
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)

    app = FastAPI(
        title="StockPulse API",
        description="AI-powered stock reaction intelligence",
        version="1.0.0",
        docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url=None
    )

    @app.exception_handler(StockPulseException)
    async def handle_sp_exception(
        request: Request,
        exc: StockPulseException
    ):
        return JSONResponse(
            status_code=400,
            content={"error": {"code": exc.code, "message": exc.message}}
        )

    setup_middleware(app, settings)
    app.include_router(api_router, prefix="/api/v1")
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    def root():
        return FileResponse("static/index.html")

    return app


app = create_app()