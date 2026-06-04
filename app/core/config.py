import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


env_path = Path(".") / ".env"
load_dotenv()

env_path = Path(".") / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    # App
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI English App")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")

    DB_USER: str = os.getenv('POSTGRES_USER')
    DB_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    DB_NAME: str = os.getenv('POSTGRES_DB')
    DB_HOST: str = os.getenv('PG_HOST')
    DB_PORT: str = os.getenv('PG_PORT')
    DATABASE_URL: str = (
        f"postgresql+psycopg2://{DB_USER}:%s@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        % quote_plus(DB_PASSWORD)
    )
    # email
    EMAIL_USER: str = os.getenv("SMTP_USER")
    EMAIL_PASS: str = os.getenv("SMTP_PASS")


    # -------------------------------------------------
    # CELERY
    # -------------------------------------------------
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # GROQ api key
    GROQ_API_KEY: str

    # Google api key
    # GOOGLE_API_KEY: str

    
    # jwt
    JWT_SECRET: str = os.getenv('JWT_SECRET')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))



settings = Settings()
