# Hackaton FIAP

### Processamento de Diagramas de Arquitetura com IA

### Alunos (6IADT)
- Luis Gustavo de Araújo Silva — RM 366233
- Vinicius Siphone Santos de Oliveira — RM 366276

---

## Arquitetura

O projeto é desenvolvido em Python com FastAPI, MongoDB como banco de dados e processamento assíncrono via Background Tasks. O serviço recebe um diagrama de arquitetura, dispara a análise em background e permite consultar o resultado pelo `job_id` retornado.

```
[Cliente]
    │
    │  POST /api/v1/analyze (multipart/form-data + x-architect-id)
    ▼
┌──────────────────────────────────────────────┐
│            AI Analysis Service               │
│                                              │
│  ┌──────────────┐                            │
│  │  Guardrail   │  valida tipo e tamanho     │
│  │  (Entrada)   │                            │
│  └──────┬───────┘                            │
│         │                                    │
│  ┌──────▼───────┐                            │
│  │  MongoDB     │  persiste job_id           │
│  │  (status:    │  status: received          │
│  │   received)  │                            │
│  └──────┬───────┘                            │
│         │  retorna job_id imediatamente      │
│         │  (status: processing)              │
│         │                                    │
│  ┌──────▼──────────────────────────────┐     │
│  │         Background Task             │     │
│  │  ┌─────────────┐  ┌─────────────┐  │     │
│  │  │File Processor│  │   Gemini    │  │     │
│  │  │(img / PDF)  │─▶│  (LLM+Visão)│  │     │
│  │  └─────────────┘  └──────┬──────┘  │     │
│  │                          │         │     │
│  │                  ┌───────▼──────┐  │     │
│  │                  │  Guardrail   │  │     │
│  │                  │  (Saída/JSON)│  │     │
│  │                  └───────┬──────┘  │     │
│  │                          │         │     │
│  │                  ┌───────▼──────┐  │     │
│  │                  │   MongoDB    │  │     │
│  │                  │ status:      │  │     │
│  │                  │ analyzed /   │  │     │
│  │                  │ error        │  │     │
│  │                  └──────────────┘  │     │
│  └─────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
    │
    │  GET /api/v1/status/{job_id} (polling)
    ▼
JSON estruturado com:
- Componentes identificados
- Riscos arquiteturais
- Recomendações
```

---

## Fluxo da Solução

1. O cliente envia um arquivo (PNG, JPG, WEBP ou PDF) via `POST /api/v1/analyze` com o header `x-architect-id`
2. O **Guardrail de Entrada** valida o tipo e o tamanho do arquivo
3. Um **job** é criado no MongoDB com status `received` e o `job_id` é retornado imediatamente
4. A análise é disparada em **background** — o cliente não precisa aguardar
5. O **File Processor** converte o arquivo para base64 (extrai a primeira página se for PDF)
6. O **Gemini Service** envia a imagem + prompt estruturado para o modelo de IA e atualiza o status para `processing`
7. O **Guardrail de Saída** valida se a resposta da IA contém todos os campos obrigatórios
8. O relatório é persistido no MongoDB com status `analyzed` ou `error`
9. O cliente consulta o resultado via `GET /api/v1/status/{job_id}`

---

## Estrutura do Projeto

```
tech-challenge-fase5/
├── app/
│   ├── main.py                  # Entrypoint FastAPI + ciclo de vida do banco
│   ├── routes/
│   │   └── analysis.py          # Endpoints REST
│   ├── services/
│   │   ├── gemini.py            # Chamada à API do Gemini + atualização de status
│   │   └── file_processor.py    # Conversão de PDF/imagem para base64
│   ├── models/
│   │   └── schemas.py           # Schemas Pydantic
│   ├── database/
│   │   ├── database.py          # Conexão assíncrona com MongoDB
│   │   └── repository.py        # Repositório de operações no banco
│   └── core/
│       ├── guardrails.py        # Validações de entrada e saída
│       └── config.py            # Configurações e variáveis de ambiente
├── tests/
│   ├── test_guardrails.py       # Testes dos guardrails
│   └── test_analysis.py         # Testes dos endpoints
├── .env.example                 # Modelo de variáveis de ambiente
├── .gitignore
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET`  | `/` | Health check geral da API |
| `POST` | `/api/v1/analyze` | Recebe um diagrama e inicia a análise em background |
| `GET`  | `/api/v1/status/{job_id}` | Consulta o status e resultado de uma análise |
| `GET`  | `/api/v1/all/diagrams` | Lista todos os diagramas do arquiteto com paginação |
| `GET`  | `/api/v1/health` | Health check do serviço de IA |

> ⚠️ Todos os endpoints exigem o header `x-architect-id` com o identificador do arquiteto responsável.

### Exemplo — `POST /api/v1/analyze`

**Requisição:**
```
POST /api/v1/analyze
x-architect-id: arq-123
Content-Type: multipart/form-data
file: diagrama.png
```

**Resposta imediata (a análise ocorre em background):**
```json
{
  "status": "processing",
  "message": "File received. Processing started in the background.",
  "job_id": "6650f1a2c3d4e5f6a7b8c9d0",
  "report": null,
  "error": null
}
```

### Exemplo — `GET /api/v1/status/{job_id}`

**Resposta após análise concluída:**
```json
{
  "job_id": "6650f1a2c3d4e5f6a7b8c9d0",
  "status": "analyzed",
  "filename": "diagrama.png",
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
  }
}
```

### Exemplo — `GET /api/v1/all/diagrams?page=1&size=10`

```json
{
  "pagination": {
    "total_records": 25,
    "current_page": 1,
    "page_size": 10,
    "total_pages": 3
  },
  "items": [
    {
      "job_id": "6650f1a2c3d4e5f6a7b8c9d0",
      "status": "analyzed",
      "filename": "diagrama.png",
      "report": { ... }
    }
  ]
}
```

### Status possíveis

| Status | Descrição |
|--------|-----------|
| `received` | Arquivo recebido, aguardando início do processamento |
| `processing` | Análise em andamento |
| `analyzed` | Análise concluída com sucesso |
| `error` | Falha durante o processamento ou análise |

---

## Pré-requisitos

- Docker e Docker Compose instalados
- Conta no [Google AI Studio](https://aistudio.google.com) com chave de API ativa

---

## Executando com Docker (recomendado)

### 1. Configuração das variáveis de ambiente

Copie o arquivo de exemplo:

```powershell
copy .env.example .env
```

Edite o `.env` com sua chave do Gemini:

```
GEMINI_API_KEY=sua_chave_aqui
MONGO_URI=mongodb://admin:password123@db:27017/?authSource=admin
```

### 2. Subindo os serviços

```bash
docker-compose up --build
```

Isso sobe dois serviços:
- **API** disponível em `http://localhost:8000`
- **MongoDB** disponível em `localhost:27017`

Documentação interativa (Swagger): `http://localhost:8000/docs`

### 3. Encerrando os serviços

```bash
docker-compose down
```

Para remover também os dados do banco:

```bash
docker-compose down -v
```

---

## Executando localmente (sem Docker)

### 1. Instalação de dependências

```powershell
py -m pip install -r requirements.txt
```

### 2. Configuração das variáveis de ambiente

```powershell
copy .env.example .env
```

Edite o `.env`:

```
GEMINI_API_KEY=sua_chave_aqui
MONGO_URI=mongodb://localhost:27017
```

### 3. Executando o serviço

```powershell
uvicorn app.main:app --reload --port 8000
```

### 4. Executando os testes

```powershell
pytest tests/ -v
```

Resultado esperado: **14 testes passando**