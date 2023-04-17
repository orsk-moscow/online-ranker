import os
from typing import Optional

from pydantic import BaseSettings

RANDOM_STATE = os.environ.get("RANDOM_STATE", 21)


class AppSettings(BaseSettings):
    """A class to hold the settings related to the App.

    Attributes:
        service_name (str): The name of the service.
        port (int): The port number the App is listening on.
        workers (int): The number of workers the App is using.
        folder (str): The folder location for the App.
        weights (str): The weights of the App.

    """

    service_name: str = "app"
    port: int = 1111
    workers: int = 1
    folder: str
    weights: str

    class Config:
        env_prefix = "APP_"


class DatabaseSettings(BaseSettings):
    """A class to hold the settings related to the database.

    Attributes:
        service_name (str): The name of the service.
        driver (str): The driver for the database.
        database (str): The name of the database.
        password (str): The password for the database.
        user (str): The user for the database.
        host (str): The host of the database.
        port (int): The port number of the database.

    """

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
    """A class to hold the settings related to the object storage.

    Attributes:
        service_name (str): The name of the service.
        access_key (str): The access key for the object storage.
        secret_key (str): The secret key for the object storage.
        bucket (str): The bucket name for the object storage.
        host (Optional[str]): The host of the object storage.
        port (Optional[int]): The port number of the object storage.
        url (str): The URL for the object storage.
        folder (str): The folder location for the object storage.
        weights (str): The weights of the object storage.

    """

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
    """A class to hold all the settings.

    Attributes:
        app (AppSettings): The App settings.
        db (DatabaseSettings): The database settings.
        s3 (ObjectStorageSettings): The object storage settings.

    """

    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    s3: ObjectStorageSettings = ObjectStorageSettings()


settings = Settings()
