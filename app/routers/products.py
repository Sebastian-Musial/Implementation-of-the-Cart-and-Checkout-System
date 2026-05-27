from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.schemas import ProductRead, ProductCreate, ProductChangeStock
from app.database import get_session
from app.models import Product

router = APIRouter()

@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, tags=["products"])
def create_product(payload: ProductCreate, session: Session = Depends(get_session)) -> Product:
    product = Product.model_validate(payload)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get("/products", response_model=list[ProductRead], status_code=status.HTTP_200_OK, tags=["products"])
def read_products(session: Session = Depends(get_session)) -> list[Product]:
    statement = select(Product).order_by(Product.product_id)
    products = session.exec(statement).all()

    return list(products)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["products"])
def delete_product(product_id: int, session: Session = Depends(get_session),) -> None:
    product = session.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    session.delete(product)
    session.commit()

    return None


@router.patch("/products/{product_id}", status_code=status.HTTP_200_OK, tags=["products"])
def change_stock_amount_product(payload: ProductChangeStock, product_id: int, session: Session = Depends(get_session),) -> Product:
    product = session.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product.amount_in_stock = payload.amount_in_stock

    session.add(product)
    session.commit()
    session.refresh(product)

    return product
