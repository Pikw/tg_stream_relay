# TG Stream Relay — Telegram Bot for Relaying Live Streams via FFmpeg

A production-ready scaffold for a Telegram bot that relays livestreams (e.g., YouTube Live) to Telegram via **FFmpeg**, with:
- **aiogram 3** (Python) bot and **Redis** queue
- **Worker** that picks up relay tasks and restreams to Telegram RTMP
- **Docker + Compose** for one-command deploy
- **Logging**, **admin notifications**, **Prometheus metrics**
- **i18n** (RU/EN) and **admin-only config/mode switching from Telegram**
- **Plugin system** for extensibility
- **Analytics dashboard** (FastAPI + Chart.js) reading stats from Redis

## Quick Start

1. Copy `.env.example` to `.env` and fill values:
```bash
cp .env.example .env
```

2. Build & start:
```bash
docker compose up -d --build
```

3. Open the dashboard at: `http://localhost:8080/` (default admin token in `.env.example`, change it!).

4. In Telegram, open your bot and send `/start`.

> To set **admin** users, put their numeric Telegram IDs in `ADMIN_IDS` (comma-separated).

### Start a Relay

1. Create a Live Stream in your Telegram channel to obtain **RTMP URL** and **Stream Key** (e.g. in the channel → “Start Live Stream” → RTMP).  
   Defaults assume `rtmp://stream.push.tlgrm.ru:443/livestream` and you pass a stream key.

2. As an admin, send command:
```
/stream_add <youtube_url_or_m3u8> <stream_key>
```
Optional flags:
- `mode=test|prod` to override current mode
- `copy=1` to try stream-copy (no re-encode), or `copy=0` to re-encode for safety

Example:
```
/stream_add https://www.youtube.com/watch?v=LIVE123 mySuperKey copy=1
```

Stop by task id:
```
/stream_stop <task_id>
```

### Modes (Test/Prod)

Switch mode globally (affects default RTMP endpoint & keys if you template them):
```
/mode test
/mode prod
```

### Config

Show config:
```
/config show
```
Set a key:
```
/config set DEFAULT_LANGUAGE en
```

### i18n

Users can switch language:
```
/setlang en
/setlang ru
```

## Files & Services

- `app/bot/main.py` — aiogram bot, handlers, plugin loader
- `app/worker/main.py` — Redis worker, invokes FFmpeg relay
- `app/dashboard/main.py` — Analytics dashboard (FastAPI + Chart.js)
- `app/utils/ffmpeg.py` — FFmpeg helpers (build & run commands)
- `app/utils/redis_client.py` — Async Redis client
- `app/i18n/localizer.py` — Simple YAML-based i18n system
- `app/notifications/notifier.py` — Admin error notifications
- `docker-compose.yml` — Services: redis, bot, worker, dashboard
- Prometheus metrics: each service exposes `:9000/metrics`

## Extending with Plugins

Drop a `.py` file into `app/bot/plugins/` with a `register(router, services)` function.
See `app/bot/plugins/example_echo.py` for a template.

## Requirements

- Docker / Docker Compose
- FFmpeg is installed inside the bot/worker images
- Redis password is required (set in `.env`)

## Notes

- YouTube relay uses `yt-dlp` to resolve the true media URL, then FFmpeg to push FLV/RTMP to Telegram.
- If `-c copy` fails due to codec mismatch, re-encoding is attempted (H.264 + AAC).

---

Licensed MIT. Built for fast customization and growth.
