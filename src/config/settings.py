from pydantic_settings import BaseSettings, SettingsConfigDict

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[2]  # goes to quiz-agent-app/

class Settings(BaseSettings):

    GROQ_API_KEY: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


    
    class Config:
        env_file = BASE_DIR / ".env"



settings = Settings()