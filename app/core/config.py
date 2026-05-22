from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    MONGO_URI: str

    class Config:
        env_file = ".env"

settings = Settings()