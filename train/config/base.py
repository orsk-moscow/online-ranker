import os
from typing import Optional
from pydantic import BaseSettings

RANDOM_STATE = os.environ.get("RANDOM_STATE", 21)


class ObjectStorageSettings(BaseSettings):
    """A settings class for object storage service.

    Attributes:
    -----------
    service_name (str): The name of the object storage service. Default is 's3'.
    access_key (str): Access key to the object storage service.
    secret_key (str): Secret key to the object storage service.
    bucket (str): The name of the bucket in the object storage service.
    host (Optional[str]): Host of the object storage service. Optional, if not provided will use the default host.
    port (Optional[int]): Port number of the object storage service. Optional, if not provided will use the default port.
    url (str): The URL of the object storage service.
    folder (str): The folder where to store the files in the object storage service.
    weights (str): The path of the weights file.

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
        # The configuration settings for the ObjectStorageSettings class.

        env_file = ".env.test"
        env_prefix = "MINIO_"


class TrainingPipelineSettings(BaseSettings):
    """A settings class for training pipeline.

    Attributes:
    -----------
    weights (str): The path of the weights file.

    """

    weights: str

    class Config:
        # The configuration settings for the TrainingPipelineSettings class.
        # TODO Training pipeline settings uses 'localhost' urls,
        # not an internal networks. Need to solve where to move it further.
        env_file = ".env.test"
        env_prefix = "TRAIN_"


class Settings(BaseSettings):
    """A settings class that contains the settings for the project.

    Attributes:
    -----------
    s3 (ObjectStorageSettings): The settings for the object storage service.
    train (TrainingPipelineSettings): The settings for the training pipeline.

    """

    s3: ObjectStorageSettings = ObjectStorageSettings()
    train: TrainingPipelineSettings = TrainingPipelineSettings()


# Creating an instance of the Settings class with the default values.
settings = Settings()
