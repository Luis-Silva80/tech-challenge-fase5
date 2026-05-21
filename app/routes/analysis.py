from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.guardrails import validate_input_file
from app.services.file_processor import file_to_base64
from app.services.gemini import analyze_diagram
from app.models.schemas import AnalysisResponse, ProcessingStatus

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_architecture(file: UploadFile = File(...)):
    """
    Endpoint principal:
    1. Valida o arquivo recebido (guardrail de entrada)
    2. Converte para base64
    3. Envia ao Gemini
    4. Valida a resposta (guardrail de saída)
    5. Retorna o relatório estruturado
    """
    file_bytes = await file.read()

    # Guardrail de entrada
    validate_input_file(file.content_type, len(file_bytes))

    try:
        image_base64, mime_type = file_to_base64(file_bytes, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        report = analyze_diagram(image_base64, mime_type)
    except ValueError as e:
        return AnalysisResponse(
            status=ProcessingStatus.ERROR,
            error=str(e)
        )
    except Exception as e:
        return AnalysisResponse(
            status=ProcessingStatus.ERROR,
            error=f"Erro inesperado na análise: {str(e)}"
        )

    return AnalysisResponse(
        status=ProcessingStatus.ANALYZED,
        report=report
    )


@router.get("/health")
async def health_check():
    """Endpoint para verificar se o serviço está no ar."""
    return {"status": "ok", "service": "ai-analysis"}