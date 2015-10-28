from logging.config import dictConfig

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'backupCount': 7,
            'filename': '/var/log/pi/smart_house_ui.log',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'urllib3': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False,
        },
        'requests': {
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False,
        },
    }
})

from smart_house_ui.main import SmartHouseApp

app = SmartHouseApp()
app.run()
