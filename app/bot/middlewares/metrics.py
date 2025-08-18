from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from typing import Callable, Dict, Any, Awaitable
from app.utils import metrics
from app.utils.redis_client import get_redis

class CommandsMetricsMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:
        if isinstance(event, Message) and event.text and event.text.startswith("/"):
            cmd = event.text.split()[0]
            metrics.commands_total.labels(cmd).inc()
            redis = await get_redis()
            await redis.incr("stats:commands")
        return await handler(event, data)
