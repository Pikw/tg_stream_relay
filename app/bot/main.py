import asyncio, os, importlib, pkgutil
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from prometheus_client import start_http_server
from loguru import logger

from app.config import settings
from app.logging_config import setup_logging
from app.utils.redis_client import get_redis
from app.i18n.localizer import Localizer
from app.bot.handlers import start as start_handlers
from app.bot.handlers import admin as admin_handlers
from app.bot.middlewares.user_locale import UserLocaleMiddleware
from app.bot.middlewares.errors import ErrorsNotifyMiddleware
from app.bot.middlewares.metrics import CommandsMetricsMiddleware

async def load_plugins(router, services):
    import app.bot.plugins as plugins_pkg
    for _, modname, ispkg in pkgutil.iter_modules(plugins_pkg.__path__):
        if not ispkg:
            mod = importlib.import_module(f"app.bot.plugins.{modname}")
            if hasattr(mod, "register"):
                mod.register(router, services)

async def main():
    setup_logging("bot", settings.log_level, logfile="bot.log")
    start_http_server(settings.bot_metrics_port)

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=RedisStorage.from_url(url=os.environ.get("REDIS_URL") or ""))

    # Services for DI
    localizer = Localizer(locales_dir=__import__("pathlib").Path(__file__).parent.parent / "i18n" / "locales",
                          default_lang=settings.default_language)
    services = {"localizer": localizer}

    # Middlewares
    dp.message.middleware(UserLocaleMiddleware(settings.default_language))
    dp.message.middleware(CommandsMetricsMiddleware())
    dp.update.outer_middleware(ErrorsNotifyMiddleware(bot, settings.admin_ids))

    # Routers
    dp.include_router(start_handlers.setup(localizer))
    dp.include_router(admin_handlers.setup(localizer))

    # Plugins
    await load_plugins(dp, services)

    await bot.set_my_commands([
        BotCommand(command="start", description="Start / Старт"),
        BotCommand(command="help", description="Help / Помощь"),
        BotCommand(command="setlang", description="Set language / Язык"),
        BotCommand(command="mode", description="[Admin] Switch mode"),
        BotCommand(command="config", description="[Admin] Config ops"),
        BotCommand(command="stream_add", description="[Admin] Start relay"),
        BotCommand(command="stream_stop", description="[Admin] Stop relay"),
        BotCommand(command="stats", description="[Admin] Stats"),
    ])

    redis = await get_redis()
    # Persist admin IDs for other services
    await redis.delete("admins:ids")
    if settings.admin_ids:
        await redis.sadd("admins:ids", *[str(i) for i in settings.admin_ids])

    logger.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
