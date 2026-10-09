
import json
import os

from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_embedding import ProductEmbedding


load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    return genai.Client(api_key=api_key)


def generate_text_embedding(text: str) -> list[float]:
    """Generate an embedding for any text, including a search query."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    client = get_gemini_client()

    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text.strip(),
        )

        if not response.embeddings:
            raise ValueError("Gemini returned no embedding")

        values = response.embeddings[0].values

        if values is None:
            raise ValueError("Gemini returned an empty embedding")

        if len(values) != 3072:
            raise ValueError(
                f"Expected 3072 dimensions, received {len(values)}"
            )

        return list(values)
    finally:
        client.close()


def build_product_text(product: Product) -> str:
    """Build a text representation of a product."""
    parts = [
        f"Product name: {product.name}",
        f"Description: {product.description}",
        f"Brand: {product.brand}",
        f"Category ID: {product.category_id}",
    ]

    if product.specifications:
        parts.append(f"Specifications: {product.specifications}")

    if product.tags:
        parts.append(f"Tags: {product.tags}")

    return "\n".join(parts)


def generate_product_embedding(product: Product) -> list[float]:
    """Generate an embedding for a product."""
    return generate_text_embedding(build_product_text(product))


def save_product_embedding(
    product: Product,
    db: Session,
) -> ProductEmbedding:
    """Generate and save/update a product embedding."""
    embedding_values = generate_product_embedding(product)

    existing_embedding = (
        db.query(ProductEmbedding)
        .filter(ProductEmbedding.product_id == product.id)
        .first()
    )

    embedding_json = json.dumps(embedding_values)

    if existing_embedding:
        existing_embedding.embedding = embedding_json
        existing_embedding.embedding_vector = embedding_values
        existing_embedding.model_name = EMBEDDING_MODEL
        db.commit()
        db.refresh(existing_embedding)
        return existing_embedding

    new_embedding = ProductEmbedding(
        product_id=product.id,
        embedding=embedding_json,
        embedding_vector=embedding_values,
        model_name=EMBEDDING_MODEL,
    )

    db.add(new_embedding)
    db.commit()
    db.refresh(new_embedding)

    return new_embedding