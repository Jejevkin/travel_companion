from logging.config import dictConfig

LOG_FORMAT = (
    '[%(asctime)s] (%(levelname)s) %(name)s '
    '[%(filename)s:%(lineno)d] => %(message)s'
)

ACCESS_LOG_FORMAT = (
    '[%(asctime)s] %(client_addr)s - "%(request_line)s" %(status_code)s'
)

LOG_DEFAULT_HANDLERS = ['console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_verbose': {
            'format': LOG_FORMAT,
        },
        'access_verbose': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': ACCESS_LOG_FORMAT,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default_verbose',
        },
        'access': {
            'class': 'logging.StreamHandler',
            'formatter': 'access_verbose',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': LOG_DEFAULT_HANDLERS,
            'level': 'INFO',
        },
        'uvicorn.error': {
            'level': 'INFO',
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': LOG_DEFAULT_HANDLERS,
    },
}


def setup_logging():
    dictConfig(LOGGING)
