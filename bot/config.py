from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: list[int] = Field(default_factory=list)

    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Contact shown when bot doesn't know the answer
    SUPPORT_USERNAME: str = "@manager"

    # How many last messages to include as context
    HISTORY_DEPTH: int = 5

    # Minimum similarity score to consider a chunk relevant (0-1)
    MIN_RELEVANCE: float = 0.4

    DB_PATH: str = "data/assistant.db"
    CHROMA_PATH: str = "data/chroma"
    KNOWLEDGE_DIR: str = "knowledge_base"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
