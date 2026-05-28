from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.schemas import OrderRead
from app.database import get_session
from app.models import Order, OrderItem


router = APIRouter()


def build_order_items_list(order: Order, session: Session) -> dict:
    statement = select(OrderItem).where(OrderItem.order_id == order.order_id)
    order_items = session.exec(statement).all()

    items = []
    
    for order_item in order_items:
        items.append(
            {
                "product_id": order_item.product_id,
                "product_name": order_item.product_name,
                "product_amount": order_item.product_amount,
                "unit_price": order_item.unit_price,
            }
        )

    return {
        "client_id": order.client_id,
        "order_id": order.order_id,
        "items": items,
        "total_order_price": order.total_order_price,
    }


@router.get("/orders/{order_id}", response_model=OrderRead, status_code=status.HTTP_200_OK, tags=["order"])
def read_order(order_id: int, session: Session = Depends(get_session)) -> dict:
    order = session.get(Order, order_id)
    
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return build_order_items_list(order, session)