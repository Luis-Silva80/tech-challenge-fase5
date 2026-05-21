import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import AnalysisReport, ArchitecturalComponent, ArchitecturalRisk, ArchitecturalRecommendation

client = TestClient(app)

MOCK_REPORT = AnalysisReport(
    components=[
        ArchitecturalComponent(
            name="API Gateway",
            type="Gateway",
            description="Ponto de entrada da API"
        )
    ],
    risks=[
        ArchitecturalRisk(
            severity="medium",
            description="Sem rate limiting configurado"
        )
    ],
    recommendations=[
        ArchitecturalRecommendation(
            priority="high",
            description="Adicionar rate limiting no gateway"
        )
    ],
    summary="Arquitetura básica com API Gateway como ponto de entrada."
)


def test_health_check():
    """Deve retornar status ok no health check."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@patch("app.routes.analysis.analyze_diagram", return_value=MOCK_REPORT)
def test_analyze_imagem_valida(mock_gemini):
    """Deve retornar status analyzed para imagem válida."""
    fake_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

    response = client.post(
        "/api/v1/analyze",
        files={"file": ("diagrama.png", fake_image, "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "analyzed"
    assert data["report"] is not None
    assert data["error"] is None


def test_analyze_tipo_invalido():
    """Deve retornar 415 para tipo de arquivo não suportado."""
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("texto.txt", b"conteudo qualquer", "text/plain")}
    )
    assert response.status_code == 415


def test_analyze_sem_arquivo():
    """Deve retornar 422 quando nenhum arquivo for enviado."""
    response = client.post("/api/v1/analyze")
    assert response.status_code == 422


@patch("app.routes.analysis.analyze_diagram", side_effect=Exception("Falha na API"))
def test_analyze_falha_na_ia(mock_gemini):
    """Deve retornar status error quando a IA falhar."""
    fake_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

    response = client.post(
        "/api/v1/analyze",
        files={"file": ("diagrama.png", fake_image, "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert data["report"] is None