from fastapi import FastAPI
from app.routes.analysis import router
from contextlib import asynccontextmanager
from app.database.database import connect_db, close_db


# Gerencia o ciclo de vida da aplicação (startup e shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # O que roda antes da API começar a aceitar requisições
    await connect_db()
    yield
    # O que roda quando a API está sendo desligada
    await close_db()

app = FastAPI(
    title="AI Architecture Analyzer",
    description="Serviço de análise automática de diagramas de arquitetura com IA",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def health_check():
    """Endpoint simples para verificar se a API está de pé."""
    return {"status": "ok", "message": "Diagram Analyzer API rodando com sucesso!"}