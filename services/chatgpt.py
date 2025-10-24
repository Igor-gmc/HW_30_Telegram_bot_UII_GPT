# --- NEW FILE: services/chatgpt.py ---

import os
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Клиент ChatGPT
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_marketing_advice(problem: str) -> str:
    """
    Возвращает совет по маркетингу, основываясь на запросе пользователя.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты опытный маркетолог, помоги кратко и чётко."},
                {"role": "user", "content": problem}
            ],
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        logger.info("Совет по маркетингу сгенерирован.")
        return answer
    except Exception as e:
        logger.error(f"Ошибка ChatGPT при получении совета: {e}")
        return "Не удалось получить совет. Попробуй позже."

async def get_motivation_phrase() -> str:
    """
    Возвращает случайную мотивационную фразу для пользователя.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты коуч по продажам. Дай короткую мотивирующую фразу."},
                {"role": "user", "content": "Мотивируй меня на успех в продажах."}
            ],
            temperature=0.9,
        )
        phrase = response.choices[0].message.content.strip()
        logger.info("Мотивационная фраза сгенерирована.")
        return phrase
    except Exception as e:
        logger.error(f"Ошибка ChatGPT при получении мотивации: {e}")
        return "Сегодня отличный день для успеха! 💪"
