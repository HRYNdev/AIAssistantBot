from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: list[int] = Field(default_factory=list)

    # LLM — works with any OpenAI-compatible API
    # OpenAI:   base_url=https://api.openai.com/v1,        model=gpt-4o-mini
    # DeepSeek: base_url=https://api.deepseek.com/v1,      model=deepseek-chat
    # Groq:     base_url=https://api.groq.com/openai/v1,   model=llama-3.3-70b-versatile
    # Ollama:   base_url=http://localhost:11434/v1,         model=llama3.2
    LLM_API_KEY: str
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"

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
