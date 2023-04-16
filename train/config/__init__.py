import os

from train.config.base import *

environment = os.environ.get("environment", "prod")

if environment == "prod":
    from train.config.prod import *
else:
    raise ValueError(f"Invalid environment: {environment}")
