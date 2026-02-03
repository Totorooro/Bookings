import uuid

from httpx import AsyncClient


async def test_register_user(ac: AsyncClient):
    unique_suffix = uuid.uuid4().hex[:8]
    email = f"kot+{unique_suffix}@pes.com"

    response = await ac.post("/auth/register", json={
        "email": email,
        "password": "kotopes",
    })

    assert response.status_code == 200