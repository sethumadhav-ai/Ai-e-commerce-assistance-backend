from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db

from app.models.user import User
from app.models.product import Product
from app.models.review import Review
from app.models.order import Order
from app.models.order_item import OrderItem

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
)


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


# ============================================================
# CREATE REVIEW
# ============================================================

@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(
        Product,
        review_data.product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    existing_review = (
        db.query(Review)
        .filter(
            Review.user_id == current_user.id,
            Review.product_id == review_data.product_id,
        )
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product",
        )

    purchased_product = (
        db.query(OrderItem)
        .join(
            Order,
            Order.id == OrderItem.order_id,
        )
        .filter(
            Order.user_id == current_user.id,
            OrderItem.product_id == review_data.product_id,
        )
        .first()
    )

    if purchased_product is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review products you have purchased",
        )

    new_review = Review(
        user_id=current_user.id,
        product_id=review_data.product_id,
        rating=review_data.rating,
        comment=review_data.comment,
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


# ============================================================
# GET REVIEWS FOR A PRODUCT
# ============================================================

@router.get(
    "/product/{product_id}",
    response_model=list[ReviewResponse],
)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(
        Product,
        product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    reviews = (
        db.query(Review)
        .filter(
            Review.product_id == product_id
        )
        .order_by(
            Review.id.desc()
        )
        .all()
    )

    return reviews


# ============================================================
# UPDATE OWN REVIEW
# ============================================================

@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = (
        db.query(Review)
        .filter(
            Review.id == review_id,
            Review.user_id == current_user.id,
        )
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    review.rating = review_data.rating
    review.comment = review_data.comment

    db.commit()
    db.refresh(review)

    return review


# ============================================================
# DELETE OWN REVIEW
# ============================================================

@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = (
        db.query(Review)
        .filter(
            Review.id == review_id,
            Review.user_id == current_user.id,
        )
        .first()
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    db.delete(review)
    db.commit()

    return None
