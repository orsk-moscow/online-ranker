from pydantic import BaseModel, conint, confloat


class SingleResponse(BaseModel):
    venue_id: conint()
    score: confloat()


class PredictResponse(BaseModel):
    venues_and_scores: list[SingleResponse]


class PingResponse(BaseModel):
    ping: str


class InputVenue(BaseModel):
    venue_id: conint()
    is_from_order_again: bool
    is_recommended: bool


class Venue(BaseModel):
    venue_id: int
    conversions_per_impression: float
    price_range: int
    rating: float
    popularity: float
    retention_rate: float
