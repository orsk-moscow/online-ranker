from pydantic import BaseModel, conint, confloat, conbool


class SingleResponse(BaseModel):
    venue_id: conint()
    score: confloat(gt=0.0, lt=1.0)


class PredictResponse(BaseModel):
    venues: list[SingleResponse]


class InputVenue(BaseModel):
    venue_id: conint()
    has_seen_venue_in_this_session: conbool()
    is_from_order_again: conbool()
    is_recommended: conbool()


class Venue(BaseModel):
    venue_id: int
    conversions_per_impression: float
    price_range: int
    rating: float
    popularity: float
    retention_rate: float
