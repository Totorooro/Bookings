from datetime import datetime
from typing import Optional
from fastapi import Cookie, Depends, Request
import jwt
from jwt.exceptions import InvalidTokenError as JWTError

from app.config import settings
from app.exceptions import IncorrectTokenFormatException, TokenAbsentException, TokenExpiredException, UserIsNotPresentException
from app.users.dao import UsersDAO
from app.users.models import Users

def get_token(booking_access_token: Optional[str] = Cookie(None)):
    return booking_access_token

async def get_current_user(token: Optional[str] = Depends(get_token)) -> Optional[Users]:
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        return None

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        return None

    user_id: str = payload.get("sub")
    if not user_id:
        return None

    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        return None
    return user


# async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
#     # if current_user.role != "admin":
#     #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#     return current_user 