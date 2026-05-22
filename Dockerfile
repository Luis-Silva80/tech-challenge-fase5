FROM python:3.11-slim

# Evita que o Python grave arquivos .pyc no disco (otimiza espaço)
ENV PYTHONDONTWRITEBYTECODE=1

# Garante que as saídas (prints e logs) apareçam no terminal em tempo real
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia primeiro apenas as dependências para aproveitar o cache de camadas do Docker
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código-fonte para dentro do contêiner
COPY . /app/

EXPOSE 8000

# Comando padrão para iniciar a API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]