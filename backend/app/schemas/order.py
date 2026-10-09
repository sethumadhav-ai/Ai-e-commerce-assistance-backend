from datetime import datetime

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    shipping_address: str = Field(
        min_length=10,
        max_length=500,
        description="Delivery address"
    )


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    payment_status: str
    shipping_address: str
    created_at: datetime
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    payment_status: str
    shipping_address: str
    created_at: datetime
    total_items: int