import pytest
from fastapi import HTTPException
from app.core.guardrails import validate_input_file, validate_output_report

# ─── Testes de validação de entrada ───────────────────────────────────────────

def test_validate_input_file_png_valido():
    """Deve aceitar PNG dentro do tamanho limite."""
    validate_input_file("image/png", 1 * 1024 * 1024)  # 1MB

def test_validate_input_file_pdf_valido():
    """Deve aceitar PDF dentro do tamanho limite."""
    validate_input_file("application/pdf", 5 * 1024 * 1024)  # 5MB

def test_validate_input_file_tipo_invalido():
    """Deve rejeitar tipos de arquivo não suportados."""
    with pytest.raises(HTTPException) as exc:
        validate_input_file("text/plain", 1024)
    assert exc.value.status_code == 415

def test_validate_input_file_muito_grande():
    """Deve rejeitar arquivos acima de 10MB."""
    with pytest.raises(HTTPException) as exc:
        validate_input_file("image/png", 11 * 1024 * 1024)  # 11MB
    assert exc.value.status_code == 413

def test_validate_input_file_gif_invalido():
    """Deve rejeitar GIF."""
    with pytest.raises(HTTPException) as exc:
        validate_input_file("image/gif", 1024)
    assert exc.value.status_code == 415


# ─── Testes de validação de saída ─────────────────────────────────────────────

def test_validate_output_report_valido():
    """Deve aceitar um relatório completo e bem estruturado."""
    report = {
        "components": [
            {"name": "API Gateway", "type": "Gateway", "description": "Entrada da API"}
        ],
        "risks": [
            {"severity": "high", "description": "Sem autenticação"}
        ],
        "recommendations": [
            {"priority": "high", "description": "Adicionar autenticação JWT"}
        ],
        "summary": "Arquitetura simples com um único ponto de entrada."
    }
    result = validate_output_report(report)
    assert result.summary == "Arquitetura simples com um único ponto de entrada."
    assert len(result.components) == 1

def test_validate_output_report_sem_componentes():
    """Deve rejeitar relatório com lista de componentes vazia."""
    report = {
        "components": [],
        "risks": [{"severity": "low", "description": "Risco x"}],
        "recommendations": [{"priority": "low", "description": "Rec x"}],
        "summary": "Resumo qualquer aqui."
    }
    with pytest.raises(ValueError, match="componente"):
        validate_output_report(report)

def test_validate_output_report_campo_ausente():
    """Deve rejeitar relatório com campos obrigatórios ausentes."""
    report = {
        "components": [
            {"name": "API", "type": "Gateway", "description": "Entrada"}
        ],
        "risks": []
        # faltam recommendations e summary
    }
    with pytest.raises(ValueError, match="ausentes"):
        validate_output_report(report)

def test_validate_output_report_summary_curto():
    """Deve rejeitar relatório com summary muito curto."""
    report = {
        "components": [
            {"name": "API", "type": "Gateway", "description": "Entrada"}
        ],
        "risks": [{"severity": "low", "description": "Risco x"}],
        "recommendations": [{"priority": "low", "description": "Rec x"}],
        "summary": "Curto"
    }
    with pytest.raises(ValueError, match="curto"):
        validate_output_report(report)