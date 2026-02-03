from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import delete, func, select, and_
from app.dao.base import BaseDAO
from app.hotels.rooms.models import Rooms
from app.database import async_session_maker



class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def find_room(cls, hotel_id: int, date_from: date, date_to: date):
        """
        SELECT 
            r.id,
            r.hotel_id,
            r.name,
            r.description,
            r.price,
            r.services,
            r.quantity,
            r.image_id,
            r.price * GREATEST(('2023-06-29'::date - '2023-06-20'::date), 1) AS total_cost,
            count_free_rooms(r.id, '2023-06-20'::date, '2023-06-29'::date) AS rooms_left
        FROM rooms r
        WHERE r.hotel_id = 1 
        AND count_free_rooms(r.id, '2023-06-20'::date, '2023-06-29'::date) >= 1;
        """
        async with async_session_maker() as session:
            query = select(
                Rooms.id, Rooms.hotel_id, Rooms.name, Rooms.description, Rooms.price, Rooms.services, Rooms.quantity, Rooms.image_id,
                (Rooms.price * func.greatest(func.date_part('day', date_to - date_from), 1)).label("total_cost"),
                (func.count_free_rooms(Rooms.id, date_from, date_to)).label("rooms_left")
            ).where(
                and_(
                    Rooms.hotel_id == hotel_id,
                    func.count_free_rooms(Rooms.id, date_from, date_to) >= 1
                    )
                )
            
            result = await session.execute(query)
            return result.mappings().all()



    @classmethod 
    async def delete_by_id(cls, room_id: int, hotel_id: int) -> None:
        """
        DELETE FROM rooms WHERE hotel_id=hotel_id and id=room_id
        """
        async with async_session_maker() as session:
            delete_query = delete(cls.model).filter_by(id=room_id, hotel_id=hotel_id)
            result = await session.execute(delete_query)
            await session.commit()

            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Комната не найдена"
                )

    
