from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.product import Product
from app.models.user import User
from app.models.wishlist import Wishlist
from app.schemas.wishlist import (
    WishlistItemCreate,
    WishlistResponse,
)


router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"],
)


def build_wishlist_response(
    user: User,
    db: Session,
) -> WishlistResponse:

    wishlist_items = (
        db.query(Wishlist)
        .filter(Wishlist.user_id == user.id)
        .order_by(Wishlist.id.desc())
        .all()
    )

    response_items = []

    for item in wishlist_items:

        product = db.get(
            Product,
            item.product_id,
        )

        if product is None:
            continue

        response_items.append(
            {
                "id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "brand": product.brand,
                "price": product.price,
                "rating": product.rating,
                "image_url": product.image_url,
            }
        )

    return WishlistResponse(
        items=response_items,
        total_items=len(response_items),
    )


@router.get(
    "/",
    response_model=WishlistResponse,
)
def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return build_wishlist_response(
        current_user,
        db,
    )


@router.post(
    "/items",
    response_model=WishlistResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_to_wishlist(
    item_data: WishlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    product = db.get(
        Product,
        item_data.product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not active",
        )

    existing_item = (
        db.query(Wishlist)
        .filter(
            Wishlist.user_id == current_user.id,
            Wishlist.product_id == item_data.product_id,
        )
        .first()
    )

    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is already in your wishlist",
        )

    wishlist_item = Wishlist(
        user_id=current_user.id,
        product_id=item_data.product_id,
    )

    db.add(wishlist_item)
    db.commit()

    return build_wishlist_response(
        current_user,
        db,
    )


@router.delete(
    "/items/{item_id}",
    response_model=WishlistResponse,
)
def remove_from_wishlist(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    wishlist_item = (
        db.query(Wishlist)
        .filter(
            Wishlist.id == item_id,
            Wishlist.user_id == current_user.id,
        )
        .first()
    )

    if wishlist_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found",
        )

    db.delete(wishlist_item)
    db.commit()

    return build_wishlist_response(
        current_user,
        db,
    )


@router.delete(
    "/",
    response_model=WishlistResponse,
)
def clear_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    (
        db.query(Wishlist)
        .filter(Wishlist.user_id == current_user.id)
        .delete()
    )

    db.commit()

    return build_wishlist_response(
        current_user,
        db,
    )