from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import delete, func, select, and_

from app.dao.base import BaseDAO
from app.hotels.models import Hotels
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def get_hotels_by_location(
        cls, date_from: date, date_to: date, location: str | None = None
    ):
        """
        SELECT h.id, h.name, h.location, h.services, h.rooms_quantity, h.image_id,
            COALESCE(SUM(count_free_rooms(r.id, '2023-01-01', '2025-07-15')), 0) AS rooms_left
        FROM hotels h
        JOIN rooms r ON r.hotel_id = h.id
        WHERE count_free_rooms(r.id, '2023-01-01', '2025-07-15') >= 1
        GROUP BY h.id, h.name, h.location, h.rooms_quantity, h.image_id
        HAVING SUM(count_free_rooms(r.id, '2023-01-01', '2025-07-15')) >= 1
        ORDER BY h.id;
        """
        async with async_session_maker() as session:
            free_rooms_count = func.count_free_rooms(Rooms.id, date_from, date_to)

            query = (
                select(
                    Hotels.id,
                    Hotels.name,
                    Hotels.location,
                    Hotels.services,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                    func.coalesce(func.sum(free_rooms_count), 0).label("rooms_left"),
                )
                .join(Rooms, Hotels.id == Rooms.hotel_id)
                .where(and_(free_rooms_count >= 1))
                .group_by(
                    Hotels.id,
                    Hotels.name,
                    Hotels.location,
                    Hotels.rooms_quantity,
                    Hotels.image_id,
                )
                .having(func.sum(free_rooms_count) >= 1)
                .order_by(Hotels.id)
            )

            if location:
                cleaned_location = location.strip()
                if cleaned_location:
                    query = query.where(Hotels.location.icontains(cleaned_location))

            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def delete_by_id(cls, hotel_id):
        async with async_session_maker() as session:
            rooms_query = (
                select(1).select_from(Rooms).filter_by(hotel_id=hotel_id).limit(1)
            )
            result = await session.execute(rooms_query)
            if result.scalar_one_or_none() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Нельзя удалить отель: в нём есть комнаты",
                )

            delete_query = delete(cls.model).filter_by(id=hotel_id)
            delete_result = await session.execute(delete_query)
            await session.commit()

            if delete_result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Отель не найден"
                )
