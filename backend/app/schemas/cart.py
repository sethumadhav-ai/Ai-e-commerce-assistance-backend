from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(
        default=1,
        ge=1,
        description="Quantity must be at least 1"
    )


class CartItemUpdate(BaseModel):
    quantity: int = Field(
        ge=1,
        description="Quantity must be at least 1"
    )


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    total_items: int
    total_price: float