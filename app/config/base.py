import os
from typing import Optional

from pydantic import BaseSettings

RANDOM_STATE = os.environ.get("RANDOM_STATE", 21)


class AppSettings(BaseSettings):
    service_name: str = "app"
    port: int = 1111
    workers: int = 1
    folder: str
    weights: str

    class Config:
        env_prefix = "APP_"


class DatabaseSettings(BaseSettings):
    service_name: str = "db"
    driver: str = "mysql"
    database: str = "venues"
    password: str = "localpassword"
    user: str = "localuser"
    host: str = "localhost"
    port: int = 3306

    class Config:
        env_prefix = "MYSQL_"


class ObjectStorageSettings(BaseSettings):
    service_name: str = "s3"
    access_key: str
    secret_key: str
    bucket: str
    host: Optional[str]
    port: Optional[int]
    url: str
    folder: str
    weights: str

    class Config:
        env_prefix = "MINIO_"


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    s3: ObjectStorageSettings = ObjectStorageSettings()


settings = Settings()
