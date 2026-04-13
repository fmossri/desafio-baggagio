from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    price: Decimal = Field(ge=0)
    quantity: int = Field(ge=0)
    active: bool = True

class ProductCreate(ProductBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Guarda-Sol G",
                    "description": "Guarda-Sol grande",
                    "price": "780.90",
                    "quantity": 1,
                    "active": True,
                }
            ]
        }
    )

class ProductUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"name": "Guarda-Sol GG"},
                {"price": "899.90", "quantity": 4},
                {"active": False},
            ]
        }
    )
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    quantity: int | None = Field(default=None, ge=0)
    active: bool | None = None

class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime

class ProductSort(str, Enum):
    CREATED_AT_DESC = "created_at_desc"
    CREATED_AT_ASC = "created_at_asc"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"

class ProductListResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Mala G",
                            "description": "Teste CRUD",
                            "price": "299.90",
                            "quantity": 12,
                            "active": True,
                            "created_at": "2026-01-01T00:00:00Z",
                            "updated_at": "2026-01-01T00:00:00Z",
                        }
                    ],
                    "total": 42,
                },
                {
                    "items": [],
                    "total": 0,
                }
            ]
        }
    )
    items: list[ProductRead]
    total: int