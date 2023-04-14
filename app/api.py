import logging
from logging.config import dictConfig

from fastapi import FastAPI, Request

import config
from app.src import models
from app.src.routers import daily, utils

__version__ = "0.0.0"

dictConfig(config.LogConfig(LOG_LEVEL="INFO").dict())
log = logging.getLogger("api")

