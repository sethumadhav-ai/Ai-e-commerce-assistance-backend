
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductResponse
from app.services.semantic_search_service import search_similar_products
from app.services.embedding_service import save_product_embedding


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# =========================================================
# Semantic Product Search
# =========================================================

@router.get("/semantic-search")
def semantic_search(
    q: str = Query(
        ...,
        min_length=2,
        max_length=500,
        description="Describe the product you want",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results",
    ),
    min_price: float | None = Query(
        default=None,
        ge=0,
        description="Minimum product price",
    ),
    max_price: float | None = Query(
        default=None,
        ge=0,
        description="Maximum product price",
    ),
    category_id: int | None = Query(
        default=None,
        ge=1,
        description="Optional product category ID",
    ),
    db: Session = Depends(get_db),
):
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price",
        )

    try:
        results = search_similar_products(
            query=q,
            db=db,
            limit=limit,
            min_price=min_price,
            max_price=max_price,
            category_id=category_id,
        )

        return {
            "query": q,
            "count": len(results),
            "filters": {
                "min_price": min_price,
                "max_price": max_price,
                "category_id": category_id,
            },
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# =========================================================
# Create Product + Automatically Generate AI Embedding
# =========================================================

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    category = db.get(
        Category,
        product_data.category_id,
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        brand=product_data.brand,
        price=product_data.price,
        stock=product_data.stock,
        rating=product_data.rating,
        category_id=product_data.category_id,
        specifications=product_data.specifications,
        tags=product_data.tags,
        image_url=product_data.image_url,
    )

    try:
        # Stage 1: Add the product and obtain its database ID.
        db.add(new_product)
        db.flush()

        # Stage 2: Generate and save its AI embedding.
        # save_product_embedding() commits internally in the
        # current implementation of embedding_service.py.
        save_product_embedding(new_product, db)

        # Stage 3: Refresh the product before returning it.
        db.refresh(new_product)

        return new_product

    except Exception as exc:
        db.rollback()

        # Do not expose internal database or API-key details.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Product creation or AI embedding generation failed. "
                "Check the backend logs for details."
            ),
        ) from exc


# =========================================================
# Get Products: Search, Filter, Sort and Pagination
# =========================================================

@router.get(
    "/",
    response_model=list[ProductResponse],
)
def get_products(
    search: str | None = Query(
        default=None,
        description="Search product names or descriptions",
    ),
    category_id: int | None = Query(
        default=None,
        ge=1,
        description="Filter by category ID",
    ),
    brand: str | None = Query(
        default=None,
        description="Filter by brand",
    ),
    min_price: float | None = Query(
        default=None,
        ge=0,
        description="Minimum product price",
    ),
    max_price: float | None = Query(
        default=None,
        ge=0,
        description="Maximum product price",
    ),
    min_rating: float | None = Query(
        default=None,
        ge=0,
        le=5,
        description="Minimum rating",
    ),
    sort_by: str = Query(
        default="id",
        description="Sort by: id, price, rating, name",
    ),
    sort_order: str = Query(
        default="asc",
        description="Sort order: asc or desc",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Products per page",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(
        Product.is_active.is_(True)
    )

    # Keyword search
    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.filter(
            Product.name.ilike(search_term)
            | Product.description.ilike(search_term)
        )

    # Validate price range
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price",
        )

    # Category filter
    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    # Brand filter
    if brand and brand.strip():
        query = query.filter(
            Product.brand.ilike(brand.strip())
        )

    # Minimum price
    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    # Maximum price
    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    # Minimum rating
    if min_rating is not None:
        query = query.filter(
            Product.rating >= min_rating
        )

    # Allowed sorting fields
    allowed_sort_fields = {
        "id": Product.id,
        "price": Product.price,
        "rating": Product.rating,
        "name": Product.name,
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_by. Use id, price, rating, or name.",
        )

    if sort_order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_order. Use asc or desc.",
        )

    sort_column = allowed_sort_fields[sort_by]

    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    offset = (page - 1) * page_size

    products = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return products


# =========================================================
# Get Product By ID
# =========================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.get(
        Product,
        product_id,
    )

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product