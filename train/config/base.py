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
    folder: str
    weights: str

    class Config:
        # Training pipeline settings uses 'localhost' urls, not an internal networks
        env_file = ".env.test"
        env_prefix = "MINIO_"


class TrainingPipelineSettings(BaseSettings):
    weights: str

    class Config:
        # Training pipeline settings uses 'localhost' urls, not an internal networks
        env_file = ".env.test"
        env_prefix = "TRAIN_"


class Settings(BaseSettings):
    s3: ObjectStorageSettings = ObjectStorageSettings()
    train: TrainingPipelineSettings = TrainingPipelineSettings()


settings = Settings()
