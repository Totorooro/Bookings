from datetime import date
from typing import List
from pydantic import BaseModel

class SBooking(BaseModel):
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int
    image_id: int | None = None
    name: str | None = None
    description: str | None = None
    services: List[str] | None = None

    class ConfigDict:
        from_attributes = True