import os, time
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from prometheus_client import start_http_server
from app.config import settings
from app.logging_config import setup_logging
from app.utils.redis_client import get_redis

app = FastAPI()
setup_logging("dashboard", settings.log_level, logfile="dashboard.log")
start_http_server(settings.dash_metrics_port)

templates = Environment(
    loader=FileSystemLoader((__import__("pathlib").Path(__file__).parent / "templates").as_posix()),
    autoescape=select_autoescape()
)

app.mount("/static", StaticFiles(directory=(__import__("pathlib").Path(__file__).parent / "static")), name="static")

def auth(request: Request):
    token = request.headers.get("X-Admin-Token") or request.query_params.get("token")
    if token != settings.dashboard_admin_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Lightweight auth via query param ?token=... or header X-Admin-Token
    try:
        auth(request)
    except HTTPException:
        return HTMLResponse("<h3>Unauthorized</h3><p>Pass ?token=YOUR_TOKEN or header X-Admin-Token</p>", status_code=401)

    redis = await get_redis()
    commands = int((await redis.get("stats:commands")) or 0)
    relays_started = int((await redis.get("stats:relays:started")) or 0)
    relays_failed = int((await redis.get("stats:relays:failed")) or 0)

    tpl = templates.get_template("index.html")
    return HTMLResponse(tpl.render(commands=commands, relays_started=relays_started, relays_failed=relays_failed, time=int(time.time())))

@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "ok"
