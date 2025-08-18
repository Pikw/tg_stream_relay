from aiogram import Router, F
from aiogram.types import Message
from app.i18n.localizer import Localizer

router = Router()

def setup(localizer: Localizer):
    @router.message(F.text == "/start")
    async def start(m: Message, user_lang: str):
        await m.answer(localizer.t("common.welcome", user_lang))

    @router.message(F.text == "/help")
    async def help_cmd(m: Message, user_lang: str):
        await m.answer(localizer.t("common.help", user_lang))

    return router
