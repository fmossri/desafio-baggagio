from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.product import Product
from app.api.deps import get_db, get_current_user
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
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
) -> Product:
    try:
        return ProductService(db).create(payload)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")

@router.get(
    "", 
    response_model=list[ProductRead], 
    status_code=status.HTTP_200_OK, 
    summary="Listar produtos", 
    response_description="Lista de produtos"
    )
def list_products(
    skip: int = Query(default=0, ge=0, le=10_000),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Product]:
    return ProductService(db).list(skip=skip, limit=limit)

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
) -> Product:
    product = ProductService(db).update(product_id, payload)
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
) -> None:
    if not ProductService(db).delete(product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")