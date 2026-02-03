from typing import List

from pydantic import BaseModel, Field


class SHotel(BaseModel):  
    id: int
    name: str
    location: str
    services: List[str] | None 
    rooms_quantity: int
    image_id: int | None 

    class ConfigDict:
        from_attributes = True 

class SHotelLocation(BaseModel):
    id: int 
    name: str
    location: str | None
    services: List[str] | None
    rooms_quantity: int
    image_id: int | None
    rooms_left: int

    class ConfigDict: 
        from_attributes = True