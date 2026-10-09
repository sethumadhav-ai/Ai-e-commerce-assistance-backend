from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


# =========================
# Create Category
# =========================

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
):
    # Check whether category already exists
    existing_category = (
        db.query(Category)
        .filter(Category.name == category_data.name)
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists",
        )

    # Create category
    new_category = Category(
        name=category_data.name,
        description=category_data.description,
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# =========================
# Get All Categories
# =========================

@router.get(
    "/",
    response_model=list[CategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
):
    categories = (
        db.query(Category)
        .order_by(Category.id)
        .all()
    )

    return categories


# =========================
# Get Category By ID
# =========================

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category