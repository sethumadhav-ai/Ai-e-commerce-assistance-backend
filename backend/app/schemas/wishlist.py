from pydantic import BaseModel


class WishlistItemCreate(BaseModel):
    product_id: int


class WishlistItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    brand: str
    price: float
    rating: float
    image_url: str | None = None


class WishlistResponse(BaseModel):
    items: list[WishlistItemResponse]
    total_items: int