import logging
from typing import Any

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import TaggedStyle
from uvicorn.logging import DefaultFormatter

from ravyn.conf import settings


class CustomFormatter(DefaultFormatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.toolkit = get_ui_toolkit()

    def formatMessage(self, record: logging.LogRecord) -> str:
        return self.toolkit.print_as_string(record.getMessage(), tag=record.levelname)


def get_log_config() -> dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": CustomFormatter,
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": CustomFormatter,
                "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


def get_ui_toolkit() -> RichToolkit:
    """
    Returns a RichToolkit instance with a custom theme for the terminal UI.
    This toolkit is used to render styled text in the terminal, enhancing the user interface
    with colors and styles for various elements like tags, placeholders, text, and errors.
    The theme is defined using a TaggedStyle for tag widths and a dictionary for colors.
    The colors are specified in a format compatible with Rich, allowing for a visually appealing
    and user-friendly terminal experience.
    The `RichToolkitTheme` is configured with specific styles for different tags and elements,
    such as "tag.title", "tag", "placeholder", "text", "selected", "result", "progress",
    "error", and "log.info". Each of these styles is defined with a foreground and background color,
    providing a consistent and readable appearance in the terminal.
    The `get_ui_toolkit` function initializes and returns this toolkit, which can be used throughout
    the application to print styled messages, logs, and other terminal outputs.
    """
    theme = RichToolkitTheme(
        style=TaggedStyle(tag_width=11),
        theme=settings.runserver_theme,
    )

    return RichToolkit(theme=theme)
