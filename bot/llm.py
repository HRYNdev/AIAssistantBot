"""LLM calls via OpenAI-compatible API.

Works with any provider that supports the OpenAI API format:
- OpenAI (gpt-4o, gpt-4o-mini)
- DeepSeek (deepseek-chat)
- Groq (llama-3.3-70b-versatile)
- Ollama (llama3.2, mistral, etc.) — set LLM_BASE_URL=http://localhost:11434/v1
- LM Studio — set LLM_BASE_URL=http://localhost:1234/v1
"""
import logging
from openai import AsyncOpenAI
from bot.config import settings

logger = logging.getLogger(__name__)
_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
    return _client


SYSTEM_PROMPT = """Ты вежливый помощник компании. Отвечай только на основе предоставленного контекста.

Правила:
- Отвечай кратко и по делу
- Используй только информацию из контекста
- Если в контексте нет ответа — ответь фразой: "НЕ_ЗНАЮ"
- Не придумывай информацию
- Отвечай на том же языке, на котором задан вопрос"""


async def ask(question: str, context_chunks: list[dict], history: list[dict]) -> str:
    """Ask LLM with context and history. Returns answer or 'НЕ_ЗНАЮ'."""
    if context_chunks:
        context = "\n\n".join(
            f"[{c['source']}]\n{c['text']}" for c in context_chunks
        )
        user_content = f"Контекст:\n{context}\n\nВопрос: {question}"
    else:
        user_content = f"Вопрос: {question}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_content})

    try:
        response = await get_client().chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("LLM API error: %s", e)
        return "НЕ_ЗНАЮ"
