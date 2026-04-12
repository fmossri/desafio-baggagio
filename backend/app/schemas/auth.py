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
                }
            ]
        }
    )
    access_token: str
    token_type: str = "bearer"
    
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