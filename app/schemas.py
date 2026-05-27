from sqlmodel import Field, SQLModel
from decimal import Decimal


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