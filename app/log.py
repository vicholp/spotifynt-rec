LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s | %(module)s:%(lineno)d | %(message)s",
        },
        "access": {
            "class": "uvicorn.logging.AccessFormatter",
            "format": '%(levelname)s | %(client_addr)s | "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
        "__main__": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
}
