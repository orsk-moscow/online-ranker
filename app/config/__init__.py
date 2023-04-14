import os

from app.config.base import *

environment = os.environ.get("environment", "prod")

if environment == "prod":
    from app.config.prod import *
else:
    raise ValueError(f"Invalid environment: {environment}")
