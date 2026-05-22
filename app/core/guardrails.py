from fastapi import HTTPException
from app.models.schemas import AnalysisReport

# Tipos de arquivo aceitos
ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "application/pdf",
}

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def validate_input_file(content_type: str, file_size: int) -> None:
    """
    Guardrail de entrada:
    - Valida tipo de arquivo
    - Valida tamanho máximo
    """
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de arquivo não suportado: {content_type}. "
                   f"Aceitos: PNG, JPG, WEBP, PDF."
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE_MB}MB."
        )

def validate_output_report(report: dict) -> AnalysisReport:
    """
    Guardrail de saída:
    - Valida se a resposta da IA tem todos os campos obrigatórios
    - Valida tipos e estrutura
    - Evita que respostas malformadas cheguem ao cliente
    """
    required_keys = {"components", "risks", "recommendations", "summary"}
    missing = required_keys - set(report.keys())

    if missing:
        raise ValueError(
            f"Resposta da IA incompleta. Campos ausentes: {missing}"
        )

    if not isinstance(report["components"], list) or len(report["components"]) == 0:
        raise ValueError("A IA não identificou nenhum componente arquitetural.")

    if not isinstance(report["risks"], list):
        raise ValueError("Campo 'risks' inválido na resposta da IA.")

    if not isinstance(report["recommendations"], list):
        raise ValueError("Campo 'recommendations' inválido na resposta da IA.")

    if not report.get("summary") or len(report["summary"]) < 10:
        raise ValueError("Resumo da análise ausente ou muito curto.")

    return AnalysisReport(**report)