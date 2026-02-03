from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Request, Response
from fastapi.templating import Jinja2Templates

from app.hotels.dao import HotelDAO
from app.hotels.router import get_hotels_by_location
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def get_main_page(request: Request, current_user: Optional[Users] = Depends(get_current_user)):
    hotels = await HotelDAO.find_all()
    return templates.TemplateResponse(
        name="index.html",
        context={"request": request, "hotels": hotels, "user": current_user}
    )


@router.get("/hotels")
async def get_hotels_page(
    request: Request,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    location: Optional[str] = None,
    current_user: Optional[Users] = Depends(get_current_user)
):
    hotels = []
    if date_from and date_to:
        hotels = await HotelDAO.get_hotels_by_location(date_from, date_to, location)
        show_rooms_left = True
    else:
        hotels = await HotelDAO.find_all()
        show_rooms_left = False
    return templates.TemplateResponse(
        name="index.html",
        context={"request": request, "hotels": hotels, "show_rooms_left": show_rooms_left, "user": current_user}
    )


@router.get("/login")
async def get_login_page(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        context={"request": request}
    )

@router.get("/register")
async def get_register_page(request: Request):
    return templates.TemplateResponse(
        name="register.html",
        context={"request": request}
    )


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")
    return {"message": "Вы успешно вышли"}