from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
from loguru import logger
from app.notifications.notifier import notify_admins

class ErrorsNotifyMiddleware(BaseMiddleware):
    def __init__(self, bot, admin_ids):
        self.bot = bot
        self.admin_ids = admin_ids

    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: Dict[str, Any]) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception("Handler error")
            await notify_admins(self.bot, self.admin_ids, f"❗️Error: {e}")
            raise
