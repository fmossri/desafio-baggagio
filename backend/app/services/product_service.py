import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import Product, OutboxEvent
from app.repositories import ProductRepository
from app.schemas import ProductCreate, ProductUpdate
from app.messaging.events import ProductEventType, ProductChangedEvent, ProductSnapshot


class ProductService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._products = ProductRepository(db)

    def create(self, payload: ProductCreate, actor_user_id: uuid.UUID) -> Product:
        if payload.quantity < 0 or payload.price < Decimal("0"):
            raise ValueError("Dados de produto inválidos")

        product = Product(
            id=uuid.uuid4(),
            name=payload.name,
            description=payload.description,
            price=payload.price,
            quantity=payload.quantity,
            active=payload.active,
            created_by=actor_user_id,
        )
        self._products.add(product)
        self._db.flush()
        self._enqueue_outbox(product, actor_user_id, ProductEventType.CREATED)
        self._db.commit()
        self._db.refresh(product)
        return product

    def get(self, product_id: uuid.UUID) -> Product | None:
        return self._products.get_by_id(product_id)

    def list(self, skip: int = 0, limit: int = 50) -> list[Product]:
        return self._products.list(skip=skip, limit=limit)

    def update(self, product_id: uuid.UUID, payload: ProductUpdate, actor_user_id: uuid.UUID) -> Product | None:
        product = self._products.get_by_id(product_id)
        if product is None:
            return None

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(product, key, value)
        
        self._enqueue_outbox(product, actor_user_id, ProductEventType.UPDATED)
        self._db.commit()
        self._db.refresh(product)
        return product

    def delete(self, product_id: uuid.UUID, actor_user_id: uuid.UUID) -> bool:
        product = self._products.get_by_id(product_id)
        if product is None:
            return False
            
        self._enqueue_outbox(product, actor_user_id, ProductEventType.DELETED)
        self._products.delete(product)
        self._db.commit()
        return True

    def _build_product_snapshot(self, product: Product) -> ProductSnapshot:
        return ProductSnapshot(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            quantity=product.quantity,
            active=product.active,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )


    def _enqueue_outbox(
        self, 
        product: Product, 
        actor_user_id: uuid.UUID, 
        event_type: ProductEventType
    ) -> None:
        event = ProductChangedEvent(
            event_id=uuid.uuid4(),
            event_type=event_type,
            occurred_at=datetime.now(timezone.utc),
            actor_user_id=actor_user_id,
            product=self._build_product_snapshot(product),
        )

        self._db.add(
            OutboxEvent(
                id=uuid.uuid4(),
                aggregate_type="product",
                aggregate_id=product.id,
                event_type=event_type.value,
                payload=event.model_dump(mode="json"),
            )
        )