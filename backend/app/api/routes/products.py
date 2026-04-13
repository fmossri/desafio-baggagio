from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models import Product, User
from app.api.deps import get_db, get_current_user
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate, ProductSort, ProductListResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)])


@router.post(
    "", 
    response_model=ProductRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Criar produto",
    response_description="Produto criado"
    )
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Product:
    try:
        return ProductService(db).create(payload, user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")


@router.get(
    "", 
    response_model=ProductListResponse, 
    status_code=status.HTTP_200_OK, 
    summary="Listar produtos", 
    response_description="Lista de produtos"
    )
def list_products(
    skip: int = Query(default=0, ge=0, le=10_000),
    limit: int = Query(default=50, ge=1, le=100),
    q: str | None = Query(default=None, min_length=1, max_length=255),
    active: bool | None = Query(default=None),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    sort: ProductSort = Query(default=ProductSort.CREATED_AT_DESC),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Min price must be less than max price")

    items, total = ProductService(db).list(
        skip=skip,
        limit=limit,
        q=q,
        active=active,
        min_price=min_price,
        max_price=max_price,
        sort=sort.value,
    )
    return ProductListResponse(
        items=[ProductRead.model_validate(item) for item in items],
        total=total,
    )


@router.get(
    "/{product_id}", 
    response_model=ProductRead, 
    status_code=status.HTTP_200_OK,
    summary="Buscar produto",
    response_description="Produto encontrado"
    )
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
) -> Product:
    product = ProductService(db).get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put(
    "/{product_id}", 
    response_model=ProductRead, 
    status_code=status.HTTP_200_OK,
    summary="Atualizar produto",
    response_description="Produto atualizado"
    )
def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Product:
    product = ProductService(db).update(product_id, payload, user.id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.delete(
    "/{product_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover produto",
    response_description="Produto removido"
    )
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    if not ProductService(db).delete(product_id, user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
