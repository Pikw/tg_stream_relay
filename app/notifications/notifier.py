from typing import Iterable
from aiogram import Bot
from loguru import logger

async def notify_admins(bot: Bot, admin_ids: Iterable[int], text: str):
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            logger.error("Failed to notify admin {}: {}", admin_id, e)
