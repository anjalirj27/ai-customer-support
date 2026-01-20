from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Application
    APP_NAME: str = "AI Customer Support"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = True

    def model_post_init(self, __context):
        if self.DATABASE_URL.startswith("postgresql://"):
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1
            )

    # AI Configuration
    AI_PROVIDER: str = "groq"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # AI Settings
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 20

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Context Management
    MAX_CONTEXT_MESSAGES: int = 10
    MAX_TOKENS_PER_CONTEXT: int = 3000

    @property
    def ai_api_key(self) -> str:
        if self.AI_PROVIDER == "groq":
            return self.GROQ_API_KEY
        return self.OPENAI_API_KEY

    @property
    def ai_model(self) -> str:
        if self.AI_PROVIDER == "groq":
            return self.GROQ_MODEL
        return self.OPENAI_MODEL

    @property
    def ai_base_url(self) -> Optional[str]:
        if self.AI_PROVIDER == "groq":
            return self.GROQ_BASE_URL
        return None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
