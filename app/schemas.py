from sqlmodel import Field, SQLModel
from decimal import Decimal



# Product
class ProductCreate(SQLModel):
    name: str = Field(min_length=1, max_length=80)
    unit_price: Decimal = Field(max_digits=6, gt=0, decimal_places=3)
    amount_in_stock: int = Field (ge=0)

class ProductRead(SQLModel):
    product_id: int
    name: str
    unit_price: Decimal = Field (decimal_places=3)
    amount_in_stock: int

class ProductChangeStock(SQLModel):
    amount_in_stock : int = Field (ge=0)



# Client
class ClientCreate(SQLModel):
    name: str = Field(min_length=1, max_length=80)
    surname: str = Field(min_length=1, max_length=80)
    phone_number: str = Field(min_length=6, max_length=26)

class ClientRead(SQLModel):
    client_id: int
    name: str
    surname: str
    phone_number: str



# Cart
class AddItemToCart(SQLModel):
    product_id: int
    product_amount: int = Field(gt = 0)

class CartItemRead(SQLModel):
    product_id: int
    product_name: str
    product_amount: int

class CartRead(SQLModel):
    client_id: int
    cart_id: int
    items: list[CartItemRead] 

class ChangeAmountProductInCart(SQLModel):
    product_amount: int = Field(gt = 0) 