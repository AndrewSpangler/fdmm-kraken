import os

DEBUG = False

APPLICATION_NAME = "FDMMHydra"
APPLICATION_DESCRIPTION = "FDMMonster Kraken setup and configuration tool"
APPLICATION_DETAILS = "GUI for FDMM Kraken cert generation and environment configuration"
AUTHOR = "Andrew Spangler"

FOOTER_TEXT = APPLICATION_DETAILS
# DEFAULT_DOMAIN = ""
ENVIRONMENT = "test"
TIMEZONE = "US/Pacific"
DOWNLOADS_DIR = "downloads"

LOADING_SPLASH = """\n"""

# # Databases
# SQLALCHEMY_POOL_SIZE = 24
# SQLALCHEMY_MAX_OVERFLOW = 5
# SQLALCHEMY_POOL_RECYCLE = 3600
# SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.getcwd(), "databases/users.sqlite")
# SQLALCHEMY_TRACK_MODIFICATIONS=False

LOGS_FOLDER = os.path.join(os.getcwd(), "logs")
LOG_FILE = os.path.join(LOGS_FOLDER, "app.log")
os.makedirs(LOGS_FOLDER, exist_ok=True)
# Logging Configuration
LOG_CONFIG = (
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s %(name)s %(threadName)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "default",
                "filename": LOG_FILE,
                "maxBytes": 1024 * 1024, # 1 MB max size
                "backupCount": 10,
                "encoding": "utf8",
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["wsgi", "file"]
        },
    }
)