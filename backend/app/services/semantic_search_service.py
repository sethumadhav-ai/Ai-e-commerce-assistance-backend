
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_embedding import ProductEmbedding
from app.services.embedding_service import generate_text_embedding


def search_similar_products(
    query: str,
    db: Session,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    category_id: int | None = None,
) -> list[dict]:
    """
    Find semantically similar products with optional price and category filters.
    """

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    if not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50")

    if min_price is not None and min_price < 0:
        raise ValueError("Minimum price cannot be negative")

    if max_price is not None and max_price < 0:
        raise ValueError("Maximum price cannot be negative")

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise ValueError("Minimum price cannot exceed maximum price")

    if category_id is not None and category_id < 1:
        raise ValueError("Category ID must be positive")

    query_vector = generate_text_embedding(query.strip())

    distance = ProductEmbedding.embedding_vector.cosine_distance(
        query_vector
    ).label("cosine_distance")

    statement = (
        select(Product, distance)
        .join(
            ProductEmbedding,
            Product.id == ProductEmbedding.product_id,
        )
        .where(
            Product.is_active.is_(True),
            ProductEmbedding.embedding_vector.is_not(None),
        )
    )

    if min_price is not None:
        statement = statement.where(Product.price >= min_price)

    if max_price is not None:
        statement = statement.where(Product.price <= max_price)

    if category_id is not None:
        statement = statement.where(Product.category_id == category_id)

    statement = statement.order_by(distance).limit(limit)

    results = db.execute(statement).all()

    return [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "brand": product.brand,
            "price": product.price,
            "stock": product.stock,
            "rating": product.rating,
            "category_id": product.category_id,
            "image_url": product.image_url,
            "similarity": round(1 - float(distance_value), 4),
        }
        for product, distance_value in results
    ]