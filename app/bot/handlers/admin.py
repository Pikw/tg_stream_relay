import json, time, uuid
from aiogram import Router, F
from aiogram.types import Message
from app.i18n.localizer import Localizer
from app.config import settings
from app.utils.redis_client import get_redis
from app.utils import metrics

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids

def setup(localizer: Localizer):
    @router.message(F.text.startswith("/setlang"))
    async def setlang(m: Message, user_lang: str):
        parts = m.text.split()
        if len(parts) < 2:
            return await m.answer(localizer.t("common.unknown", user_lang))
        lang = parts[1].strip().lower()
        redis = await get_redis()
        await redis.set(f"user:lang:{m.from_user.id}", lang)
        await m.answer(localizer.t("common.language_set", user_lang, lang=lang))

    @router.message(F.text.startswith("/mode"))
    async def mode(m: Message, user_lang: str):
        if not is_admin(m.from_user.id):
            return await m.answer(localizer.t("common.not_allowed", user_lang))
        parts = m.text.split()
        if len(parts) >= 2:
            mode = parts[1].strip().lower()
            if mode in ("test", "prod"):
                redis = await get_redis()
                await redis.set("config:mode", mode)
                return await m.answer(localizer.t("admin.mode_switched", user_lang, mode=mode))
        await m.answer(localizer.t("common.unknown", user_lang))

    @router.message(F.text.startswith("/config"))
    async def config_cmd(m: Message, user_lang: str):
        if not is_admin(m.from_user.id):
            return await m.answer(localizer.t("common.not_allowed", user_lang))
        parts = m.text.split(maxsplit=3)
        redis = await get_redis()
        if len(parts) == 2 and parts[1] == "show":
            cfg = await redis.hgetall("config")
            if not cfg:
                cfg = {}
            lines = [localizer.t("admin.config_item", user_lang, k=k, v=v) for k, v in cfg.items()]
            return await m.answer("\n".join(lines) or "(empty)")
        if len(parts) >= 4 and parts[1] == "set":
            k, v = parts[2], parts[3]
            await redis.hset("config", k, v)
            return await m.answer(localizer.t("admin.config_set", user_lang, k=k, v=v))
        await m.answer(localizer.t("common.unknown", user_lang))

    @router.message(F.text.startswith("/stats"))
    async def stats_cmd(m: Message, user_lang: str):
        if not is_admin(m.from_user.id):
            return await m.answer(localizer.t("common.not_allowed", user_lang))
        redis = await get_redis()
        # Basic counters from Redis (optional)
        commands = int((await redis.get("stats:commands")) or 0)
        relays_started = int((await redis.get("stats:relays:started")) or 0)
        relays_failed = int((await redis.get("stats:relays:failed")) or 0)
        await m.answer(localizer.t("admin.stats", user_lang, commands=commands, relays_started=relays_started, relays_failed=relays_failed))

    @router.message(F.text.startswith("/stream_add"))
    async def stream_add(m: Message, user_lang: str):
        if not is_admin(m.from_user.id):
            return await m.answer(localizer.t("common.not_allowed", user_lang))
        # /stream_add <url> <stream_key> [mode=test|prod] [copy=1|0]
        parts = m.text.split()
        if len(parts) < 3:
            return await m.answer(localizer.t("common.unknown", user_lang))
        url = parts[1]
        stream_key = parts[2]
        mode = (await (await get_redis()).get("config:mode")) or settings.mode
        copy_flag = True
        for p in parts[3:]:
            if p.startswith("mode="):
                mode = p.split("=",1)[1]
            if p.startswith("copy="):
                copy_flag = p.split("=",1)[1] == "1"

        rtmp_url = settings.rtmp_url_test if mode == "test" else settings.rtmp_url_prod

        task_id = str(uuid.uuid4())
        payload = {
            "task_id": task_id,
            "type": "start",
            "url": url,
            "rtmp_url": rtmp_url,
            "stream_key": stream_key,
            "copy": copy_flag,
            "created_at": int(time.time()),
            "notify_chat": m.chat.id
        }
        redis = await get_redis()
        await redis.lpush("stream:queue", json.dumps(payload))
        await redis.incr("stats:relays:started")
        await m.answer(localizer.t("admin.stream_added", user_lang, task_id=task_id))

    @router.message(F.text.startswith("/stream_stop"))
    async def stream_stop(m: Message, user_lang: str):
        if not is_admin(m.from_user.id):
            return await m.answer(localizer.t("common.not_allowed", user_lang))
        parts = m.text.split()
        if len(parts) < 2:
            return await m.answer(localizer.t("common.unknown", user_lang))
        task_id = parts[1]
        redis = await get_redis()
        await redis.publish("stream:control", json.dumps({"action":"stop","task_id":task_id}))
        await m.answer(localizer.t("admin.stream_stopped", user_lang, task_id=task_id))

    return router
