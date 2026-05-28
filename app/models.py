from sqlmodel import Field, SQLModel
#from enum import Enum
from decimal import Decimal
from datetime import datetime
from sqlalchemy import UniqueConstraint

#Enum
#class cart_status(str, enum):
#class order_status(str, enum):


#SQL model
class Product(SQLModel, table=True):
    __tablename__ = "products"

    product_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=80)
    unit_price: Decimal = Field(max_digits=6, gt=0, decimal_places=3)
    amount_in_stock: int = Field (default=0, ge=0)


class Client(SQLModel, table=True):
    __tablename__ = "clients"
        
    client_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=80)
    surname: str = Field(min_length=1, max_length=80)
    phone_number: str = Field(min_length=6, max_length=26)


class Cart(SQLModel, table=True):
    __tablename__ = "carts"

    cart_id: int | None = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="clients.client_id", index=True, unique=True)
    #Status: cart_status 


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_id_product_id"),
    )

    cart_item_id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="carts.cart_id", index=True)
    product_id: int = Field(foreign_key="products.product_id", index=True)
    product_amount: int = Field(gt=0)


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    order_id: int | None = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="clients.client_id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    #status: order_status 
    total_order_price: Decimal = Field(max_digits=10, gt=0, decimal_places=3)


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    order_item_id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.order_id", index=True)
    product_id: int = Field(foreign_key="products.product_id", index=True)
    product_name: str = Field(min_length=1, max_length=80)
    product_amount: int = Field(gt= 0)
    unit_price: Decimal = Field(max_digits=6, gt=0, decimal_places=3)