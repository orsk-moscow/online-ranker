from pydantic import BaseModel, conint, confloat


class SingleResponse(BaseModel):
    """A response containing the score of a single venue."""

    venue_id: conint()  # The unique identifier of the venue
    score: confloat()  # The score of the venue, represented as a float


class PredictResponse(BaseModel):
    """A response containing a list of venues and their scores."""

    venues_and_scores: list[SingleResponse]  # A list of SingleResponse objects


class PingResponse(BaseModel):
    """A response confirming that the server is alive."""

    ping: str  # A string message indicating that the server is alive


class InputVenue(BaseModel):
    """An input venue with its corresponding attributes."""

    venue_id: conint()  # The unique identifier of the venue
    is_from_order_again: bool  # A boolean indicating whether the venue is from a previous order
    is_recommended: bool  # A boolean indicating whether the venue is recommended


class Venue(BaseModel):
    """A venue with its attributes."""

    venue_id: int  # The unique identifier of the venue
    conversions_per_impression: float  # The ratio of conversions to impressions
    price_range: int  # The price range of the venue
    rating: float  # The average rating of the venue
    popularity: float  # The popularity of the venue
    retention_rate: float  # The rate of retention for the venue's customers
