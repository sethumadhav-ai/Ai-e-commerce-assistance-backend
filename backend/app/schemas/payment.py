from datetime import datetime

from pydantic import BaseModel


class PaymentCreate(BaseModel):
    order_id: int


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_provider: str
    payment_intent_id: str | None
    amount: float
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True