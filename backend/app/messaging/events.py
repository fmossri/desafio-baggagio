import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class ProductEventType(str, Enum):
    CREATED = "product.created"
    UPDATED = "product.updated"
    DELETED = "product.deleted"


class ProductSnapshot(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    price: Decimal
    quantity: int
    active: bool
    created_at: datetime
    updated_at: datetime

class ProductChangedEvent(BaseModel):
    event_id: uuid.UUID
    event_type: ProductEventType
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_user_id: uuid.UUID
    product: ProductSnapshot

    def routing_key(self) -> str:
        return self.event_type.value