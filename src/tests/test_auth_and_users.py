import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    user_data = {
        "username": f"test_{uuid.uuid4().hex[:6]}",
        "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
        "password": "stringst",
    }
    response = await client.post("/api/users/register/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert isinstance(uuid.UUID(data["id"]), uuid.UUID)
    assert data["is_active"] is True
    assert data["is_superuser"] is False

    return user_data


@pytest.mark.asyncio
async def test_auth_tokens(client: AsyncClient):
    user_data = {
        "username": f"auth_{uuid.uuid4().hex[:6]}",
        "email": f"auth_{uuid.uuid4().hex[:6]}@example.com",
        "password": "stringst",
    }
    reg_response = await client.post("/api/users/register/", json=user_data)
    assert reg_response.status_code == 201

    login_data = {"login": user_data["username"], "password": user_data["password"]}
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["token_type"] == "bearer"
    return {"user": user_data, "tokens": data}


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    auth_data = await test_auth_tokens(client)
    old_refresh = auth_data["tokens"]["refresh_token"]

    response = await client.post(
        "/api/auth/token/refresh", json={"refresh_token": old_refresh}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] != old_refresh


@pytest.mark.asyncio
async def test_login_with_username(client: AsyncClient):
    auth_data = await test_auth_tokens(client)
    user_data = auth_data["user"]

    response = await client.post(
        "/api/auth/login",
        json={"login": user_data["username"], "password": user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_with_email(client: AsyncClient):
    auth_data = await test_auth_tokens(client)
    user_data = auth_data["user"]

    response = await client.post(
        "/api/auth/login",
        json={"login": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
