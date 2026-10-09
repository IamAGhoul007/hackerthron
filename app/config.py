from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    log_json: bool = False
    cors_origins: str = "http://localhost:8000"
    admin_api_key: str = "change-me-admin-key"
    rate_limit_per_min: int = 30
    
    llm_provider: str = "groq"
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
