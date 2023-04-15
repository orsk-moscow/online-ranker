import logging
from pathlib import Path

import boto3
from config import settings
from fastapi import FastAPI, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src import models, schemas

log = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

db = settings.db
url = f"{db.driver}://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}"
engine = create_engine(url)
log.info(f"Connected to database: {db.host}:{db.port}/{db.database}")
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)


def get_venue(db: Session, venue_id: int):
    log.info(f"Getting venue: {venue_id}")
    return db.query(models.Venue).filter(models.Venue.venue_id == venue_id).first()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def download_weigths():

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
