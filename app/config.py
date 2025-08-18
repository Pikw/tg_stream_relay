from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    bot_token: str = Field(env="BOT_TOKEN")
    admin_ids: List[int] = Field(default_factory=list, env="ADMIN_IDS")
    default_language: str = Field(default="ru", env="DEFAULT_LANGUAGE")
    mode: str = Field(default="prod", env="MODE")  # "test" | "prod"
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    redis_host: str = Field(default="redis", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")

    rtmp_url_test: str = Field(default="rtmp://stream.push.tlgrm.ru:443/livestream", env="RTMP_URL_TEST")
    rtmp_url_prod: str = Field(default="rtmp://stream.push.tlgrm.ru:443/livestream", env="RTMP_URL_PROD")
    stream_key_test: str = Field(default="", env="STREAM_KEY_TEST")
    stream_key_prod: str = Field(default="", env="STREAM_KEY_PROD")

    bot_metrics_port: int = Field(default=9000, env="BOT_METRICS_PORT")
    worker_metrics_port: int = Field(default=9001, env="WORKER_METRICS_PORT")
    dash_metrics_port: int = Field(default=9002, env="DASH_METRICS_PORT")
    dash_http_port: int = Field(default=8080, env="DASH_HTTP_PORT")

    dashboard_admin_token: str = Field(default="changeme", env="DASHBOARD_ADMIN_TOKEN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

def redis_url() -> str:
    if settings.redis_password:
        return f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
    return f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
