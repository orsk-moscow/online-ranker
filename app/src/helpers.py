import logging
from pathlib import Path

import boto3
from catboost import CatBoostRanker
from config import settings
from fastapi import FastAPI, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src import models

log = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

db = settings.db
url = f"{db.driver}://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}"
engine = create_engine(url)
log.info(f"Connected to database: {db.host}:{db.port}/{db.database}")
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)


def get_venues(db: Session, venue_ids: list[int]) -> list[models.Venue]:
    """
    Retrieve a list of venues from the database given their ids.

    Args:
        db (Session): SQLAlchemy database session.
        venue_ids (list[int]): List of venue ids to retrieve.

    Returns:
        list[models.Venue]: List of Venue objects.
    """
    return db.query(models.Venue).filter(models.Venue.venue_id.in_(venue_ids)).all()


def get_db():
    """
    Get a database session for the current request context.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def download_weigths():
    """
    Download weights from S3 and store them in a local folder.

    Returns:
        str: Absolute path to the downloaded weights file.
    """
    s3_settings = settings.s3
    s3_client = boto3.client(
        service_name=s3_settings.service_name,
        endpoint_url=s3_settings.url,
        aws_access_key_id=s3_settings.access_key,
        aws_secret_access_key=s3_settings.secret_key,
    )

    app_settings = settings.app
    folder = Path(f"{app_settings.folder}")
    folder.mkdir(parents=True, exist_ok=True)
    local_path = folder.joinpath(app_settings.weights)

    log.info(f"Downloading weights from S3: {s3_settings.bucket}/{s3_settings.folder}/{s3_settings.weights}")
    s3_client.download_file(
        s3_settings.bucket,
        f"{s3_settings.folder}/{s3_settings.weights}",
        str(local_path.absolute()),
    )
    log.info(f"Downloaded weights into: {local_path.absolute()}")
    return local_path.absolute()


def rows_to_dict(rows: list[models.Venue]) -> dict[int, list]:
    """
    Convert a list of Venue objects to a dictionary with venue ids as keys and
    a list of feature values as values.

    Args:
        rows (list[models.Venue]): List of Venue objects.

    Returns:
        dict[int, list]: Dictionary with venue ids as keys and feature values as values.
    """
    return dict(
        [
            (
                row.venue_id,
                [
                    row.conversions_per_impression,
                    row.price_range,
                    row.rating,
                    row.popularity,
                    row.retention_rate,
                ],
            )
            for row in rows
        ]
    )


def get_ranker(request: Request):
    """
    Retrieve the CatBoostRanker model from the application state.

    Args:
        request (Request): FastAPI request object.

    Returns:
        CatBoostRanker: CatBoostRanker model.
    """
    return request.app.state.ranker


def on_startup(app: FastAPI) -> None:
    """
    Function to be called on application startup.

    Downloads the CatBoostRanker model from S3 and initializes it.

    Args:
        app (FastAPI): FastAPI application object.

    Returns:
        None
    """
    path = download_weigths()
    log.info("Ranker dependency: initializing")
    app.state.ranker = CatBoostRanker().load_model(path)
