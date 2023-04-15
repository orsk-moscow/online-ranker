import logging
from logging.config import dictConfig

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session

import config
from src import models, schemas
from src.helpers import SessionLocal, engine, get_venue, get_db, download_weigths
from src.schemas import InputVenue, PingResponse, PredictResponse
import boto3

__version__ = "0.0.0"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("api")

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

download_weigths()


@app.post("/predict", response_model=PredictResponse)
def predict(
    session_id: constr(),
    is_new_user: bool,
    venues: list[InputVenue],
    db: Session = Depends(get_db),
):
    # improvement: select all venues in one query:
    [get_venue(db, venue) for venue in venues]
    return PredictResponse(venues=[{"venue_id": 1, "score": 0.5}])


@app.get("/ping", response_model=PingResponse)
def ping():
    return {"ping": "pong"}
