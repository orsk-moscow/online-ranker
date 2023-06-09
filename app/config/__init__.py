import os

from config.base import *

environment = os.environ.get("environment", "prod")

if environment == "prod":
    from config.prod import *
else:
    raise ValueError(f"Invalid environment: {environment}")
