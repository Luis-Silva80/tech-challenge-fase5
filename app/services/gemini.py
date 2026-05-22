import json
import google.generativeai as genai
from app.core.config import settings
from app.core.guardrails import validate_output_report
from app.models.schemas import AnalysisReport, ProcessingStatus
from bson import ObjectId
from app.database.database import get_db

genai.configure(api_key=settings.GEMINI_API_KEY)

PROMPT_TEMPLATE = """
Você é um especialista em arquitetura de software. Analise o diagrama de arquitetura fornecido e retorne SOMENTE um JSON válido, sem explicações, sem markdown, sem blocos de código.

O JSON deve seguir EXATAMENTE esta estrutura:

{
  "components": [
    {
      "name": "nome do componente",
      "type": "tipo (ex: API Gateway, Banco de Dados, Serviço, Fila, etc)",
      "description": "descrição breve do papel deste componente"
    }
  ],
  "risks": [
    {
      "severity": "high | medium | low",
      "description": "descrição do risco arquitetural identificado"
    }
  ],
  "recommendations": [
    {
      "priority": "high | medium | low",
      "description": "recomendação de melhoria arquitetural"
    }
  ],
  "summary": "resumo geral da arquitetura analisada em 2 a 4 frases"
}

Regras obrigatórias:
- Retorne APENAS o JSON, sem nenhum texto antes ou depois
- Identifique ao menos 1 componente
- Identifique ao menos 1 risco
- Identifique ao menos 1 recomendação
- Se a imagem não for um diagrama de arquitetura, retorne um JSON com summary explicando isso e listas vazias
"""

async def analyze_diagram(image_base64: str, mime_type: str, job_id: str) -> AnalysisReport:
    """
    Envia o diagrama ao Gemini e retorna o relatório validado.
    """
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    image_part = {
        "inline_data": {
            "mime_type": mime_type,
            "data": image_base64,
        }
    }
    
    db = get_db()
    
    # 1. Atualiza o status para "processando"
    await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": ProcessingStatus.PROCESSING}}
    )

    response = model.generate_content([PROMPT_TEMPLATE, image_part])

    raw_text = response.text.strip()

    # Remove blocos de markdown caso o modelo desobedeça
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]

    try:
        report_dict = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Resposta da IA não é um JSON válido: {e}\nResposta: {raw_text}")
  
    try:
      # Guardrail de saída
      report = validate_output_report(report_dict)
      await db.jobs.update_one(
          {"_id": ObjectId(job_id)},
          {"$set": {
              "status": ProcessingStatus.ANALYZED,
              "relatorio": report.model_dump()
          }}
      )
    except ValueError as e:
      await db.jobs.update_one(
          {"_id": ObjectId(job_id)},
          {"$set": {
              "status": ProcessingStatus.ERROR,
              "erro": e
          }}
      )
    except Exception as e:
      await db.jobs.update_one(
          {"_id": ObjectId(job_id)},
          {"$set": {
              "status": ProcessingStatus.ERROR,
              "exception": e
          }}
      )