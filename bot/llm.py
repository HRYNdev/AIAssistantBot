"""Groq LLM calls."""
import logging
from groq import AsyncGroq
from bot.config import settings

logger = logging.getLogger(__name__)
_client: AsyncGroq | None = None


def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.GROQ_API_KEY)
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
            model=settings.GROQ_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Groq API error: %s", e)
        return "НЕ_ЗНАЮ"
