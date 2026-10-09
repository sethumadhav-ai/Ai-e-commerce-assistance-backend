from datetime import datetime

from pydantic import BaseModel, Field


class InteractionCreate(BaseModel):
    product_id: int

    interaction_type: str = Field(
        min_length=1,
        max_length=50,
        description="Examples: view, search, wishlist, cart, purchase, review"
    )


class InteractionResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    interaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True