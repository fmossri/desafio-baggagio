import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        return self._db.get(Product, product_id)

    def list(self, skip: int = 0, limit: int = 50) -> list[Product]:
        statement = select(Product).offset(skip).limit(limit).order_by(Product.created_at.desc())
        return list(self._db.scalars(statement).all())

    def add(self, product: Product) -> Product:
        self._db.add(product)
        self._db.flush()
        return product

    def delete(self, product: Product) -> None:
        self._db.delete(product)