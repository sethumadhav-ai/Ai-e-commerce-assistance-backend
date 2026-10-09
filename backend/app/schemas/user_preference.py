from datetime import datetime

from pydantic import BaseModel, Field


class UserPreferenceCreate(BaseModel):
    preferred_categories: str | None = Field(
        default=None,
        max_length=1000
    )

    preferred_brands: str | None = Field(
        default=None,
        max_length=1000
    )

    preferred_price_range: str | None = Field(
        default=None,
        max_length=100
    )

    interests: str | None = Field(
        default=None,
        max_length=2000
    )


class UserPreferenceUpdate(BaseModel):
    preferred_categories: str | None = Field(
        default=None,
        max_length=1000
    )

    preferred_brands: str | None = Field(
        default=None,
        max_length=1000
    )

    preferred_price_range: str | None = Field(
        default=None,
        max_length=100
    )

    interests: str | None = Field(
        default=None,
        max_length=2000
    )


class UserPreferenceResponse(BaseModel):
    id: int
    user_id: int
    preferred_categories: str | None
    preferred_brands: str | None
    preferred_price_range: str | None
    interests: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True