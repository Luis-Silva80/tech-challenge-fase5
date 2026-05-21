# Hackaton FIAP

### Processamento de Diagramas de Arquitetura com IA

### Alunos (6IADT)
- Luis Gustavo de Araújo Silva — RM 366233
- Vinicius Siphone Santos de Oliveira — RM 366276

## Arquitetura

O projeto é desenvolvido em Python com FastAPI. Ele é chamado pelo serviço de backend via HTTP e retorna um JSON estruturado com o resultado da análise.

```
[Serviço de Backend]
        │
        │  POST /api/v1/analyze (multipart/form-data)
        ▼
┌──────────────────────────────────────────┐
│          AI Analysis Service             │
│                                          │
│  ┌──────────────┐   ┌─────────────────┐  │
│  │  Guardrail   │   │ File Processor  │  │
│  │  (Entrada)   │──▶│ (imagem / PDF)  │  │
│  └──────────────┘   └───────┬─────────┘  │
│                             │            │
│                    ┌────────▼────────┐   │
│                    │ Gemini Service  │   │
│                    │ (LLM + Visão)   │   │
│                    └────────┬────────┘   │
│                             │            │
│                    ┌────────▼────────┐   │
│                    │  Guardrail      │   │
│                    │  (Saída / JSON) │   │
│                    └────────┬────────┘   │
└─────────────────────────────┼────────────┘
                              │
                              ▼
                  JSON estruturado com:
                  - Componentes identificados
                  - Riscos arquiteturais
                  - Recomendações
```

---

## Fluxo da Solução

1. O serviço de backend envia um arquivo (PNG, JPG, WEBP ou PDF) via `POST /api/v1/analyze`
2. O **Guardrail de Entrada** valida o tipo e o tamanho do arquivo
3. O **File Processor** converte o arquivo para base64 (extrai a primeira página se for PDF)
4. O **Gemini Service** envia a imagem + prompt estruturado para o modelo de IA
5. O **Guardrail de Saída** valida se a resposta da IA contém todos os campos obrigatórios
6. O serviço retorna um JSON estruturado com status, relatório ou erro

## Estrutura do Projeto

```
tech-challenge-fase5/
├── app/
│   ├── main.py                  # Entrypoint FastAPI
│   ├── routes/
│   │   └── analysis.py          # Endpoints REST
│   ├── services/
│   │   ├── gemini.py            # Chamada à API do Gemini
│   │   └── file_processor.py    # Conversão de PDF/imagem
│   ├── models/
│   │   └── schemas.py           # Schemas Pydantic
│   └── core/
│       ├── guardrails.py        # Validações de entrada e saída
│       └── config.py            # Configurações e variáveis de ambiente
├── tests/
│   ├── test_guardrails.py       # Testes dos guardrails
│   └── test_analysis.py         # Testes dos endpoints
├── .env.example                 # Modelo de variáveis de ambiente
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/analyze` | Recebe um diagrama e retorna o relatório de análise |
| `GET` | `/api/v1/health` | Verifica se o serviço está no ar |

### Exemplo de resposta — `POST /api/v1/analyze`

```json
{
  "status": "analyzed",
  "report": {
    "components": [
      {
        "name": "Amazon API Gateway",
        "type": "API Gateway",
        "description": "Ponto de entrada para as requisições da API."
      }
    ],
    "risks": [
      {
        "severity": "medium",
        "description": "Ausência de segmentação de rede entre frontend e backend."
      }
    ],
    "recommendations": [
      {
        "priority": "high",
        "description": "Implementar VPC Network ACLs para controle de tráfego."
      }
    ],
    "summary": "Arquitetura distribuída na AWS com múltiplos serviços gerenciados."
  },
  "error": null
}
```

### Status possíveis

| Status | Descrição |
|--------|-----------|
| `analyzed` | Análise concluída com sucesso |
| `error` | Falha durante o processamento ou análise |

## Pré-requisitos

- Python 3.10+
- `pip`
- Conta no [Google AI Studio](https://aistudio.google.com) com chave de API ativa

### Instalação de dependências

Na raiz do projeto, execute:

```powershell
py -m pip install -r requirements.txt
```

### Configuração das variáveis de ambiente

Copie o arquivo de exemplo e preencha com sua chave:

```powershell
copy .env.example .env
```

Edite o `.env`:

```
GEMINI_API_KEY=sua_chave_aqui
```

### Executando o serviço

```powershell
uvicorn app.main:app --reload --port 8001
```

O serviço estará disponível em `http://localhost:8001`

Documentação interativa (Swagger): `http://localhost:8001/docs`

### Executando os testes

```powershell
pytest tests/ -v
```
