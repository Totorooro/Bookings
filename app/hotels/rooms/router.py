from datetime import date
from fastapi import APIRouter, HTTPException, Query

from app.hotels.dao import HotelDAO
from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import SRooms


router = APIRouter(prefix="/hotels", tags=["Комнаты"])

@router.get("/{hotel_id}/rooms")
async def get_rooms(hotel_id: int, date_from: date = Query(..., description="Дата заезда"), date_to: date = Query(..., description="Дата выезда")) -> list[SRooms]:
    hotel = await HotelDAO.find_one_or_none(id=hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Отель не найден")
    return await RoomDAO.find_room(hotel_id, date_from, date_to)


@router.delete("/{hotel_id}/rooms/{room_id}", status_code=204)
async def delete_room(room_id: int, hotel_id: int):
    hotel = await HotelDAO.find_one_or_none(id=hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Отель не найден")
    
    await RoomDAO.delete_by_id(room_id, hotel_id)