from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from app.utils.redis_client import get_redis

class UserLocaleMiddleware(BaseMiddleware):
    def __init__(self, default_lang: str):
        self.default = default_lang

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:
        user = getattr(event, "from_user", None) or data.get("event_from_user")
        redis = await get_redis()
        lang = self.default
        if user:
            stored = await redis.get(f"user:lang:{user.id}")
            if stored:
                lang = stored
        data["user_lang"] = lang
        return await handler(event, data)
