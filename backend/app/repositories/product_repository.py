import uuid
from decimal import Decimal

from sqlalchemy import select, asc, desc, func
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        return self._db.get(Product, product_id)

    def list(
        self, 
        skip: int = 0, 
        limit: int = 50,
        q: str | None = None,
        active: bool | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort: str = "created_at_desc",
        ) -> tuple[list[Product], int]:
        statement = select(Product)
        statement = self._apply_filters(statement, q=q, active=active, min_price=min_price, max_price=max_price)
        statement = self._apply_sort(statement, sort)

        count_statement = select(func.count()).select_from(statement.subquery())
        total = int(self._db.scalar(count_statement) or 0)

        page_statement = statement.offset(skip).limit(limit)
        rows = list(self._db.scalars(page_statement).all())
        return rows, total

    def add(self, product: Product) -> Product:
        self._db.add(product)
        self._db.flush()
        return product

    def delete(self, product: Product) -> None:
        self._db.delete(product)


    @staticmethod
    def _apply_filters(
        statement,
        *,
        q: str | None,
        active: bool | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
    ):
        if q is not None and q.strip():
            escaped = q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            statement = statement.where(Product.name.ilike(f"%{escaped}%", escape="\\"))
        if active is not None:
            statement = statement.where(Product.active.is_(active))
        if min_price is not None:
            statement = statement.where(Product.price >= min_price)
        if max_price is not None:
            statement = statement.where(Product.price <= max_price)
        return statement

    @staticmethod
    def _apply_sort(statement, sort: str):
        key = (sort or "created_at_desc").lower()
        match key:
            case "created_at_asc":
                return statement.order_by(asc(Product.created_at))
            case "price_asc":
                return statement.order_by(asc(Product.price), asc(Product.id))
            case "price_desc":
                return statement.order_by(desc(Product.price), desc(Product.id))
            case "name_asc":
                return statement.order_by(asc(Product.name), asc(Product.id))
            case "name_desc":
                return statement.order_by(desc(Product.name), desc(Product.id))
            case _default:
                return statement.order_by(desc(Product.created_at), asc(Product.id))