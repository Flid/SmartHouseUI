#!/usr/bin/env python

import os
from logging.config import dictConfig

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {"default": {"level": "DEBUG", "formatter": "standard"}},
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "urllib3": {"handlers": ["default"], "level": "WARN", "propagate": False},
        "requests": {"handlers": ["default"], "level": "WARN", "propagate": False},
    },
}

if os.path.isdir("/var/log/"):
    LOGGING["handlers"]["default"].update(
        {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "backupCount": 7,
            "filename": "/var/log/pi/smart_house_ui.log",
        }
    )
else:
    LOGGING["handlers"]["default"].update({"class": "logging.StreamHandler"})

dictConfig(LOGGING)


from smart_house_ui.main import SmartHouseApp  # noqa isort:skip
app = SmartHouseApp()
app.run()
