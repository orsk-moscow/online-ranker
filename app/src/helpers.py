import logging

import boto3
from config import settings
from fastapi import FastAPI, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from . import models, schemas

log = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)


def get_venue(db: Session, venue_id: int):
    return db.query(models.Venue).filter(models.Venue.venue_id == venue_id).first()


def get_maker(request: Request):
    return request.app.state.maker


def on_startup(app: FastAPI) -> None:
    log.info("s3 dependency: initializing")
    app.state.s3 = boto3.client(
        service_name=settings.s3.service_name,
        endpoint_url=settings.s3.url,
        aws_access_key_id=settings.s3.access_key,
        aws_secret_access_key=settings.s3.secret_key,
    )

    log.info("database dependency: initializing")
    db = settings.db
    url = f"{db.driver}://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}?autocommit=true"
    app.state.db = create_engine(url)
