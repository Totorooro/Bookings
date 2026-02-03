from datetime import date
from sqlalchemy import and_, insert, select, or_, func
from sqlalchemy.exc import SQLAlchemyError

from app.logger import logger
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def find_booking(cls, user_id: int):
        """
        SELECT b.room_id, b.user_id, b.date_from, b.date_to, b.price, b.total_cost, b.total_days, r.image_id, r.description, r.services
        FROM Bookings b
        JOIN Rooms r ON b.id = r.id
        WHERE user_id=1
        """
        async with async_session_maker() as session: # type: ignore[attr-defined]
            query = (
                select(
                    Bookings.room_id,
                    Bookings.user_id,
                    Bookings.date_from,
                    Bookings.date_to,
                    Bookings.price,
                    Bookings.total_cost,
                    Bookings.total_days,
                    Rooms.image_id,
                    Rooms.name,
                    Rooms.description,
                    Rooms.services,
                )
                .join(Rooms, Bookings.room_id == Rooms.id)
                .where(Bookings.user_id == user_id)
            )

            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def delete_by_id(cls, booking_id: int, user_id: int) -> bool:
        booking = await cls.find_one_or_none(id=booking_id, user_id=user_id)
        if not booking:
            return False

        async with async_session_maker() as session: # type: ignore[attr-defined]
            delete_query = Bookings.__table__.delete().where( # type: ignore[attr-defined]
                Bookings.id == booking_id, Bookings.user_id == user_id
            )
            await session.execute(delete_query)
            await session.commit()
            return True

    @classmethod
    async def add(cls, user_id: int, room_id: int, date_from: date, date_to: date): # type: ignore[attr-defined]
        try:
            async with async_session_maker() as session: # type: ignore[attr-defined]
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )

                get_rooms_left = (
                    select(Rooms.quantity - func.count(booked_rooms.c.room_id))
                    .select_from(Rooms)
                    .outerjoin(booked_rooms, booked_rooms.c.room_id == Rooms.id)
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                # print(get_rooms_left.compile(engine, compile_kwargs={"literal_binds": True}))

                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar() # type: ignore[attr-defined]

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar() # type: ignore[attr-defined]
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings)
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                else:
                    return None
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }

            logger.error(msg, extra=extra, exc_info=True)
