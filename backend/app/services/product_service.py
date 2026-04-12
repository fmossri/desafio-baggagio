import uuid
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models import Product
from app.repositories import ProductRepository
from app.schemas import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._products = ProductRepository(db)

    def create(self, payload: ProductCreate) -> Product:
        if payload.quantity < 0 or payload.price < Decimal("0"):
            raise ValueError("Dados de produto inválidos")

        product = Product(
            id=uuid.uuid4(),
            name=payload.name,
            description=payload.description,
            price=payload.price,
            quantity=payload.quantity,
            active=payload.active,
        )
        self._products.add(product)
        self._db.commit()
        self._db.refresh(product)
        return product

    def get(self, product_id: uuid.UUID) -> Product | None:
        return self._products.get_by_id(product_id)

    def list(self, skip: int = 0, limit: int = 50) -> list[Product]:
        return self._products.list(skip=skip, limit=limit)

    def update(self, product_id: uuid.UUID, payload: ProductUpdate) -> Product | None:
        product = self._products.get_by_id(product_id)
        if product is None:
            return None

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(product, key, value)
        
        self._db.commit()
        self._db.refresh(product)
        return product

    def delete(self, product_id: uuid.UUID) -> bool:
        product = self._products.get_by_id(product_id)
        if product is None:
            return False
            
        self._products.delete(product)
        self._db.commit()
        return True