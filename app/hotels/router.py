import asyncio
from datetime import date
from typing import List
from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache
from pydantic import parse_obj_as

from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotel, SHotelLocation

router = APIRouter(prefix="/hotels", tags=["Отели"])

@router.get("/id/{hotel_id}", response_model=List[SHotel])
async def get_hotels(hotel_id: int):
    return await HotelDAO.find_all(id=hotel_id)


@router.delete("/{hotel_id}", status_code=204)
async def delete_hotel(hotel_id: int):
    await HotelDAO.delete_by_id(hotel_id)


@router.get("/location", response_model=List[SHotelLocation])
@cache(expire=20)
async def get_hotels_by_location(
    date_from: date = Query(...),
    date_to: date = Query(...),
    location: str | None = Query(None)
):
    await asyncio.sleep(3)
    return await HotelDAO.get_hotels_by_location(date_from, date_to, location)

@router.get("", response_model=List[SHotel])
async def get_all_hotels():
    return await HotelDAO.find_all()