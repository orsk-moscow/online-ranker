import os
from typing import Optional
from pydantic import BaseSettings

RANDOM_STATE = os.environ.get("RANDOM_STATE", 21)


class ObjectStorageSettings(BaseSettings):
    service_name: str = "s3"
    access_key: str
    secret_key: str
    bucket: str
    host: Optional[str]
    port: Optional[int]
    url: str

    class Config:
        # TODO change to .env
        env_file = ".env.test"
        env_prefix = "MINIO_"


class Settings(BaseSettings):
    s3: ObjectStorageSettings = ObjectStorageSettings()


settings = Settings()
