import asyncio, json, time, signal, contextlib
from loguru import logger
from prometheus_client import start_http_server
from yt_dlp import YoutubeDL

from app.config import settings
from app.logging_config import setup_logging
from app.utils.redis_client import get_redis
from app.utils.ffmpeg import build_ffmpeg_cmd, run_ffmpeg
from app.utils import metrics

RUNNING: dict[str, asyncio.subprocess.Process] = {}
STOP = False

async def resolve_input_url(url: str) -> str:
    # If it's a YouTube (or similar) URL, resolve with yt-dlp to a direct media URL
    if any(dom in url for dom in ["youtube.com", "youtu.be", "twitch.tv", "vk.com"]):
        ydl_opts = {"quiet": True, "noplaylist": True, "skip_download": True, "format": "best"}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("url") or url
    return url

async def consumer():
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe("stream:control")

    async def control_listener():
        async for msg in pubsub.listen():
            if msg.get("type") != "message":
                continue
            try:
                data = json.loads(msg["data"])
            except Exception:
                continue
            if data.get("action") == "stop":
                task_id = data.get("task_id")
                proc = RUNNING.get(task_id)
                if proc:
                    logger.info("Stopping task {}", task_id)
                    with contextlib.suppress(ProcessLookupError):
                        proc.terminate()
                else:
                    await redis.set(f"stream:stop:{task_id}", "1", ex=3600)

    asyncio.create_task(control_listener())

    while not STOP:
        item = await redis.brpop("stream:queue", timeout=5)
        if not item:
            await asyncio.sleep(0.1)
            continue
        _, raw = item
        try:
            payload = json.loads(raw)
        except Exception as e:
            logger.error("Bad payload: {}", e)
            continue

        task_id = payload["task_id"]
        url = payload["url"]
        rtmp_url = payload["rtmp_url"]
        stream_key = payload["stream_key"]
        copy_flag = payload.get("copy", True)
        notify_chat = payload.get("notify_chat")

        start_ts = time.time()
        metrics.relays_active.inc()
        try:
            input_url = await resolve_input_url(url)
            cmd = build_ffmpeg_cmd(input_url, rtmp_url, stream_key, copy=copy_flag)

            def on_line(line: str):
                if "Error" in line or "error" in line:
                    logger.warning("[FFmpeg] {}", line)

            rc = await run_ffmpeg(cmd, on_line=on_line)
            if rc != 0:
                metrics.relays_failed.inc()
            else:
                logger.info("Relay finished successfully")
        except Exception as e:
            metrics.relays_failed.inc()
            logger.exception("Relay failed")
            # Notify admins via bot is out-of-process; store in Redis for bot polling if needed
            await redis.lpush("events:errors", json.dumps({"ts": int(time.time()), "err": str(e)}))
        finally:
            metrics.relays_active.dec()
            metrics.relay_duration.observe(time.time() - start_ts)

async def main():
    setup_logging("worker", settings.log_level, logfile="worker.log")
    start_http_server(settings.worker_metrics_port)
    await consumer()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
