from typing import Optional
from pydantic import BaseSettings


class AppSettings(BaseSettings):
    service_name: str = "app"
    port: int = 1111
    workers: int = 1

    class Config:
        env_prefix = "APP_"


class DatabaseSettings(BaseSettings):
    service_name: str = "db"
    driver: str = "mysql"
    database: str
    password: str
    user: str
    host: str
    port: int

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

    class Config:
        env_prefix = "MINIO_"


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    s3: ObjectStorageSettings = ObjectStorageSettings()


settings = Settings()
