from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from decimal import Decimal

from app.schemas import CartItemRead, CartRead, AddItemToCart, ChangeAmountProductInCart, OrderRead
from app.database import get_session
from app.models import Cart, CartItem, Product, OrderItem, Order


router = APIRouter()




def build_cart_items_list(cart: Cart, session: Session) -> dict:
    statement = select(CartItem).where(CartItem.cart_id == cart.cart_id)
    cart_items = session.exec(statement).all()

    items = []

    for cart_item in cart_items:
        product = session.get(Product, cart_item.product_id)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product assigned to cart item not found",
            )

        items.append(
            {
                "product_id": product.product_id,
                "product_name": product.name,
                "product_amount": cart_item.product_amount,
            }
        )

    return {
        "client_id": cart.client_id,
        "cart_id": cart.cart_id,
        "items": items,
    }


@router.get("/carts/{cart_id}", response_model=CartRead, status_code=status.HTTP_200_OK, tags=["cart"])
def read_cart(cart_id: int,session: Session = Depends(get_session)) -> dict:
    cart = session.get(Cart, cart_id)
    
    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    return build_cart_items_list(cart, session)


@router.post("/carts/{cart_id}/items", response_model=CartRead, status_code=status.HTTP_201_CREATED, tags=["cart"])
def add_item_or_update_item_in_cart(cart_id: int, payload: AddItemToCart, session: Session = Depends(get_session)) -> dict:
    cart = session.get(Cart, cart_id)

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )
    
    product = session.get(Product, payload.product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    statement = select(CartItem).where(
        CartItem.cart_id == cart_id,
        CartItem.product_id == payload.product_id,
    )

    cart_item = session.exec(statement).first()

    if cart_item is None:
        cart_item = CartItem(
            cart_id=cart_id,
            product_id=payload.product_id,
            product_amount=payload.product_amount,
        )
        session.add(cart_item)
    else:
        cart_item.product_amount += payload.product_amount
        session.add(cart_item)

    session.commit()

    return build_cart_items_list(cart, session)


# @router.delete("/carts/{cart_id}/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["cart"])
# def delete_cart_item(cart_id: int, product_id: int, session: Session = Depends(get_session),) -> None:
#     cart = session.get(Cart, cart_id)

#     if cart is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Cart not found",
#         )
    
#     statement = select(CartItem).where(
#         CartItem.cart_id == cart_id,
#         CartItem.product_id == product_id,
#     )

#     cart_item = session.exec(statement).first()

#     if cart_item  is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Item not found in cart",
#         )

#     session.delete(cart_item)
#     session.commit()

#     return None


@router.patch("/carts/{cart_id}/items/{product_id}", response_model=CartRead, status_code=status.HTTP_200_OK, tags=["cart"])
def change_amount_product_in_cart(payload: ChangeAmountProductInCart, cart_id: int,  product_id: int, session: Session = Depends(get_session),) -> dict:
    cart = session.get(Cart, cart_id)

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    statement = select(CartItem).where(
        CartItem.cart_id == cart_id,
        CartItem.product_id == product_id,
    )

    cart_item = session.exec(statement).first()

    if cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart",
        )

    cart_item.product_amount = payload.product_amount

    session.add(cart_item)
    session.commit()

    return build_cart_items_list(cart, session)

@router.post("/carts/{cart_id}/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED, tags=["cart"])
def checkout_cart(cart_id: int, session: Session = Depends(get_session)) -> dict:
    try:   
        cart = session.get(Cart, cart_id)
        
        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found",
            )
        
        statement = select(CartItem).where(CartItem.cart_id == cart_id)
        cart_items = session.exec(statement).all()


        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )
        
        checkout_items = []
        total_order_price = Decimal("0")

        for cart_item in cart_items:
            product_statement = (
                select(Product)
                .where(Product.product_id == cart_item.product_id)
                .with_for_update()
            )

            product = session.exec(product_statement).first()

            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {cart_item.product_id} not found",
                )

            if product.amount_in_stock < cart_item.product_amount:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Not enough stock for product '{product.name}'",
                )

            total_order_price += product.unit_price * cart_item.product_amount

            checkout_items.append(
                {
                    "cart_item": cart_item,
                    "product": product,
                }
            )

        order = Order(
            client_id=cart.client_id,
            total_order_price=total_order_price,
        )

        session.add(order)
        session.flush()

        order_id = order.order_id
        client_id = cart.client_id

        response_items = []

        for item in checkout_items:
            cart_item = item["cart_item"]
            product = item["product"]

            product.amount_in_stock -= cart_item.product_amount

            order_item = OrderItem(
                order_id=order_id,
                product_id=product.product_id,
                product_name=product.name,
                product_amount=cart_item.product_amount,
                unit_price=product.unit_price,
            )

            session.add(product)
            session.add(order_item)

            response_items.append(
                {
                    "product_id": product.product_id,
                    "product_name": product.name,
                    "product_amount": cart_item.product_amount,
                    "unit_price": product.unit_price,
                }
            )

        for cart_item in cart_items:
            session.delete(cart_item)

        session.commit()

        return {
            "client_id": client_id,
            "order_id": order_id,
            "items": response_items,
            "total_order_price": total_order_price,
        }

    except HTTPException:
        session.rollback()
        raise

    except Exception:
        session.rollback()
        raise