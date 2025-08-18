from aiogram import Router, F
from aiogram.types import Message

def register(router: Router, services: dict):
    @router.message(F.text.startswith("/echo"))
    async def echo(m: Message):
        await m.answer(m.text.replace("/echo", "", 1).strip() or "…")
