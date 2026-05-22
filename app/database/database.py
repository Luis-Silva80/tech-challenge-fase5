import os
from motor.motor_asyncio import AsyncIOMotorClient

# Captura a URI das variáveis de ambiente geradas pelo Docker Compose
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password123@db:27017/?authSource=admin")

# Variáveis globais para armazenar a conexão
client = None
db = None

async def connect_db():
    global client, db
    # Inicia o client assíncrono
    client = AsyncIOMotorClient(MONGO_URI)
    # Define o nome do banco de dados (será criado automaticamente no primeiro insert)
    db = client["diagram_analyzer_db"]

async def close_db():
    global client
    if client:
        client.close()

def get_db():
    """
    Função utilitária para ser injetada nas rotas do FastAPI,
    garantindo acesso à instância correta do banco.
    """
    return db