from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Header, Query
from app.core.guardrails import validate_input_file
from app.services.file_processor import file_to_base64
from app.services.gemini import analyze_diagram
from app.models.schemas import AnalysisResponse, ProcessingStatus
from app.database.repository import JobRepository
import math

router = APIRouter()

# Instância do nosso repositório
repo = JobRepository()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_architecture(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    x_architect_id: str = Header(..., description="ID do arquiteto responsável")
):    
    if x_architect_id == '':
        raise HTTPException(status_code=422, detail='You must inform the x_architect_id')
    
    file_bytes = await file.read()

    # Guardrail de entrada
    validate_input_file(file.content_type, len(file_bytes))
    
    # Cria o registro inicial no banco de dados
    novo_job = {
        "nome_arquivo": file.filename,
        "status": ProcessingStatus.RECEIVED,
        "x_architect_id": x_architect_id,
        "relatorio": None
    }

    # Uso do Repositório:
    job_id = await repo.insert_one(novo_job)

    try:
        image_base64, mime_type = file_to_base64(file_bytes, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Dispara a tarefa em background, passando o ID do job
    background_tasks.add_task(analyze_diagram, image_base64, mime_type, job_id)

    return AnalysisResponse(
        status=ProcessingStatus.PROCESSING,
        message='File received. Processing started in the background.',
        job_id=job_id
    )

@router.get("/status/{job_id}")
async def check_status(job_id: str, x_architect_id: str = Header(..., description="ID do arquiteto responsável")):
    
    if not x_architect_id.strip():
        raise HTTPException(status_code=422, detail='You must inform the x-architect-id')
        
    # Busca o job no banco de dados
    job = await repo.find_one({"_id": job_id, "x_architect_id": x_architect_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
        
    return {
        "job_id": str(job["_id"]),
        "status": job["status"],
        "nome_arquivo": job["nome_arquivo"],
        "relatorio": job.get("relatorio")
    }

@router.get("/all/diagrams")
async def get_all_diagrams(
    x_architect_id: str = Header(..., description="ID do arquiteto responsável"),
    page: int = Query(1, ge=1, description="Número da página atual"),
    size: int = Query(10, ge=1, le=100, description="Quantidade de itens por página")
):
    if not x_architect_id.strip():
        raise HTTPException(status_code=422, detail='You must inform the x-architect-id')
        
    query_filter = {"x_architect_id": x_architect_id}
    skip = (page - 1) * size
    
    # Uso do Repositório:
    total_records = await repo.count_documents(query_filter)
    jobs_do_banco = await repo.find(query_filter, skip=skip, limit=size)
    
    skip = (page - 1) * size
    
    jobs_formatados = []
    for job in jobs_do_banco:
        jobs_formatados.append({
            "job_id": str(job["_id"]),
            "status": job["status"],
            "nome_arquivo": job.get("nome_arquivo", "Desconhecido"),
            "relatorio": job.get("relatorio")
        })
        
    return {
        "pagination": {
            "total_records": total_records,
            "current_page": page,
            "page_size": size,
            "total_pages": math.ceil(total_records / size) if total_records > 0 else 0
        },
        "items": jobs_formatados
    }

@router.get("/health")
async def health_check():
    """Endpoint para verificar se o serviço está no ar."""
    return {"status": "ok", "service": "ai-analysis"}