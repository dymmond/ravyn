from __future__ import annotations

import logging
import sys
from typing import Any

from loguru import logger

from ravyn.conf.enums import EnvironmentType
from ravyn.types import LifeSpanHandler

from ..configs.settings import AppSettings


async def start_database(): ...


async def close_database(): ...


class InterceptHandler(logging.Handler):  # pragma: no cover
    def emit(self, record: logging.LogRecord) -> None:
        level: str
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


class DevelopmentSettings(AppSettings):
    # the environment can be names to whatever you want.
    environment: str = EnvironmentType.DEVELOPMENT
    debug: bool = True
    reload: bool = True

    def __init__(self, *args: Any, **kwds: Any):
        super().__init__(*args, **kwds)
        logging_level = logging.DEBUG if self.debug else logging.INFO
        loggers = ("palfrey.asgi", "palfrey.access", "ravyn")
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=logging_level)]

        logger.configure(handlers=[{"sink": sys.stderr, "level": logging_level}])

    @property
    def on_startup(self) -> list[LifeSpanHandler]:
        """
        List of events/actions to be done on_startup.
        """
        return [start_database]

    @property
    def on_shutdown(self) -> list[LifeSpanHandler]:
        """
        List of events/actions to be done on_shutdown.
        """
        return [close_database]
