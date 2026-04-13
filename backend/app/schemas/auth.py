from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict

class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "fulano@exemplo.com",
                    "password": "senha123",
                }
            ]
        }
    )
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIuLi4ifQ.signature",
                    "token_type": "bearer",
                    "refresh_token": "nK8mP2xQvR5tL7wHj3Bf6NsZc9Ud4Ea1oI0xY5kW8pL2qV7nT4rU3sE6zA2bC5dF8gH1jK4mN7pQ0rS3vX6yZ9aB2cE5fG8hJ1kM4nP7qR0tU3wX6yZ9",
                }
            ]
        }
    )
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None

class RefreshRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "refresh_token": "nK8mP2xQvR5tL7wHj3Bf6NsZc9Ud4Ea1oI0xY5kW8pL2qV7nT4rU3sE6zA2bC5dF8gH1jK4mN7pQ0rS3vX6yZ9aB2cE5fG8hJ1kM4nP7qR0tU3wX6yZ9",
                }
            ]
        }
    )
    refresh_token: str

class LogoutRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIuLi4ifQ.signature",
                    "refresh_token": "nK8mP2xQvR5tL7wHj3Bf6NsZc9Ud4Ea1oI0xY5kW8pL2qV7nT4rU3sE6zA2bC5dF8gH1jK4mN7pQ0rS3vX6yZ9aB2cE5fG8hJ1kM4nP7qR0tU3wX6yZ9",
                }
            ]
        }
    )
    access_token: str
    refresh_token: str | None = None

class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "examples": [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "fulano@exemplo.com",
                "is_active": True,
            }
        ]
    })

    id: UUID
    email: EmailStr
    is_active: bool