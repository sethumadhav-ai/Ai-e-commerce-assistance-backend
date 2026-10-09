from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db

from app.models.user import User
from app.models.user_preference import UserPreference

from app.schemas.user_preference import (
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
)


router = APIRouter(
    prefix="/preferences",
    tags=["User Preferences"],
)


# GET CURRENT USER PREFERENCES
@router.get(
    "/",
    response_model=UserPreferenceResponse,
)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preferences = (
        db.query(UserPreference)
        .filter(
            UserPreference.user_id == current_user.id
        )
        .first()
    )

    if preferences is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )

    return preferences


# CREATE USER PREFERENCES
@router.post(
    "/",
    response_model=UserPreferenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_preferences(
    preference_data: UserPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_preferences = (
        db.query(UserPreference)
        .filter(
            UserPreference.user_id == current_user.id
        )
        .first()
    )

    if existing_preferences:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User preferences already exist",
        )

    new_preferences = UserPreference(
        user_id=current_user.id,
        preferred_categories=preference_data.preferred_categories,
        preferred_brands=preference_data.preferred_brands,
        preferred_price_range=preference_data.preferred_price_range,
        interests=preference_data.interests,
    )

    db.add(new_preferences)
    db.commit()
    db.refresh(new_preferences)

    return new_preferences


# UPDATE USER PREFERENCES
@router.put(
    "/",
    response_model=UserPreferenceResponse,
)
def update_preferences(
    preference_data: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preferences = (
        db.query(UserPreference)
        .filter(
            UserPreference.user_id == current_user.id
        )
        .first()
    )

    if preferences is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )

    preferences.preferred_categories = (
        preference_data.preferred_categories
    )

    preferences.preferred_brands = (
        preference_data.preferred_brands
    )

    preferences.preferred_price_range = (
        preference_data.preferred_price_range
    )

    preferences.interests = (
        preference_data.interests
    )

    db.commit()
    db.refresh(preferences)

    return preferences


# DELETE USER PREFERENCES
@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preferences = (
        db.query(UserPreference)
        .filter(
            UserPreference.user_id == current_user.id
        )
        .first()
    )

    if preferences is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found",
        )

    db.delete(preferences)
    db.commit()

    return None