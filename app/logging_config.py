import logging
from logging.handlers import RotatingFileHandler
import sys
from loguru import logger

def setup_logging(name: str, level: str = "INFO", logfile: str | None = None):
    # Bridge standard logging to loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except Exception:
                level = record.levelno
            logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    logger.remove()
    logger.add(sys.stdout, level=level, backtrace=False, diagnose=False, enqueue=True)
    if logfile:
        logger.add(RotatingFileHandler(logfile, maxBytes=5_000_000, backupCount=3),
                   level=level, enqueue=True, backtrace=False, diagnose=False)
    logger.bind(service=name).info(f"Logging initialized for {name}")
    return logger
