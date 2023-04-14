from pydantic import BaseModel, conbool, constr

from app.src.models import PredictResponse, InputVenue
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(
    session_id: constr(),
    is_new_user: conbool(),
    venues: list[InputVenue],
):
    return PredictResponse(venues=[{"venue_id": 1, "score": 0.5}])
