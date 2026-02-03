from sqlalchemy import JSON, Column, Integer, String, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class Rooms(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    hotel_id = Column(ForeignKey("hotels.id"))
    name = Column(String)
    description = Column(String)
    price = Column(Integer) 
    services = Column(JSON)
    quantity = Column(Integer)
    image_id = Column(Integer) 


    hotel = relationship("Hotels", back_populates="room")
    booking = relationship("Bookings", back_populates="room")

    def __str__(self):
        return f"Номер {self.name}"