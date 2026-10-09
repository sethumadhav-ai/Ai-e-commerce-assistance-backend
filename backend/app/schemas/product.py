from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str
    description: str
    brand: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    rating: float = Field(default=0.0, ge=0, le=5)
    category_id: int
    specifications: str | None = None
    tags: str | None = None
    image_url: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True