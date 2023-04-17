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

# create the database tables based on the models
models.Base.metadata.create_all(bind=engine)

# create a FastAPI application
app = FastAPI(title="venues-ranker", version=__version__)


@app.post("/predict", response_model=PredictResponse)
def predict(
    is_new_user: bool,
    venues: list[InputVenue],
    db: Session = Depends(get_db),  # get a database session using a dependency
    ranker: CatBoostRanker = Depends(get_ranker),  # get a CatBoostRanker model using a dependency
):
    """Predict the ranking score of a list of venues.

    Arguments:
        is_new_user (bool): Whether the user is new or returning.
        venues (list[InputVenue]): A list of InputVenue objects.

    Keyword Arguments:
        db (Session): A database session (default: {Depends(get_db)}).
        ranker (CatBoostRanker): A CatBoostRanker model (default: {Depends(get_ranker)}).

    Returns:
        PredictResponse: A response containing a list of venues sorted by their predicted score.
    """
    # retrieve data about the venues from the database
    sql_rows = get_venues(db, [venue.venue_id for venue in venues])
    sql_dict = rows_to_dict(sql_rows)

    # create input data for the ranker model
    data = [
        [is_new_user, venue.is_from_order_again, venue.is_recommended] + sql_dict[venue.venue_id] for venue in venues
    ]

    # predict the score for each venue using the ranker model
    predictions = ranker.predict(data).tolist()

    # return the venues and their scores, sorted by score in descending order
    venues_and_scores = [
        {"venue_id": venue.venue_id, "score": prediction} for venue, prediction in zip(venues, predictions)
    ]
    venues_and_scores.sort(key=lambda x: x["score"], reverse=True)
    return PredictResponse(venues_and_scores=venues_and_scores)


@app.get("/ping", response_model=PingResponse)
def ping():
    """A simple ping endpoint.

    Returns:
        PingResponse: A response containing a "pong" message.
    """
    return {"ping": "pong"}


# run the on_startup function to set up any necessary initialization
on_startup(app)
