from datetime import datetime
from decimal import Decimal
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