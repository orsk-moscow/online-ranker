from pydantic import BaseModel, conint, confloat


class SingleResponse(BaseModel):
    venue_id: conint()
    score: confloat(gt=0.0, lt=1.0)


class PredictResponse(BaseModel):
    venues: list[SingleResponse]


class PingResponse(BaseModel):
    ping: str


class InputVenue(BaseModel):
    venue_id: conint()
    has_seen_venue_in_this_session: bool
    is_from_order_again: bool
    is_recommended: bool


class Venue(BaseModel):
    venue_id: int
    conversions_per_impression: float
    price_range: int
    rating: float
    popularity: float
    retention_rate: float
