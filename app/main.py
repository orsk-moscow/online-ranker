import logging

from catboost import CatBoostRanker
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from src import models
from src.helpers import rows_to_dict, engine, get_db, get_ranker, get_venues, on_startup
from src.schemas import InputVenue, PingResponse, PredictResponse

__version__ = "0.0.0"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("api")

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="venues-ranker", version=__version__)


@app.post("/predict", response_model=PredictResponse)
def predict(
    is_new_user: bool,
    venues: list[InputVenue],
    db: Session = Depends(get_db),
    ranker: CatBoostRanker = Depends(get_ranker),
):
    sql_rows = get_venues(db, [venue.venue_id for venue in venues])
    sql_dict = rows_to_dict(sql_rows)
    data = [
        [is_new_user, venue.is_from_order_again, venue.is_recommended] + sql_dict[venue.venue_id] for venue in venues
    ]
    predictions = ranker.predict(data).tolist()
    venues_and_scores = [
        {"venue_id": venue.venue_id, "score": prediction} for venue, prediction in zip(venues, predictions)
    ]
    return PredictResponse(venues_and_scores=venues_and_scores)


@app.get("/ping", response_model=PingResponse)
def ping():
    return {"ping": "pong"}


on_startup(app)
