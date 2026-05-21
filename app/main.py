from fastapi import FastAPI
from app.routes.analysis import router

app = FastAPI(
    title="AI Architecture Analyzer",
    description="Serviço de análise automática de diagramas de arquitetura com IA",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")