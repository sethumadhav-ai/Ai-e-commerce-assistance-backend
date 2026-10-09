from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db

from app.models.user import User
from app.models.product import Product
from app.models.user_product_interaction import UserProductInteraction

from app.schemas.user_product_interaction import (
    InteractionCreate,
    InteractionResponse,
)


router = APIRouter(
    prefix="/interactions",
    tags=["Product Interactions"],
)


ALLOWED_INTERACTIONS = {
    "view",
    "search",
    "wishlist",
    "cart",
    "purchase",
    "review",
}


# RECORD PRODUCT INTERACTION
@router.post(
    "/",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_interaction(
    interaction_data: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check that the interaction type is valid
    interaction_type = interaction_data.interaction_type.strip().lower()

    if interaction_type not in ALLOWED_INTERACTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid interaction_type. "
                "Use: view, search, wishlist, cart, purchase, or review"
            ),
        )

    # Check that the product exists
    product = db.get(
        Product,
        interaction_data.product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Create interaction
    new_interaction = UserProductInteraction(
        user_id=current_user.id,
        product_id=interaction_data.product_id,
        interaction_type=interaction_type,
    )

    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)

    return new_interaction


# GET CURRENT USER'S INTERACTIONS
@router.get(
    "/",
    response_model=list[InteractionResponse],
)
def get_my_interactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    interactions = (
        db.query(UserProductInteraction)
        .filter(
            UserProductInteraction.user_id == current_user.id
        )
        .order_by(
            UserProductInteraction.id.desc()
        )
        .all()
    )

    return interactions