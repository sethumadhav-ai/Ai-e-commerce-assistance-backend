from app.db.session import get_db
from app.models.product import Product
from app.services.embedding_service import (
    save_product_embedding,
)


db = next(get_db())

try:
    product = db.get(Product, 50)

    if product is None:
        print("Product 50 was not found.")
    else:
        print("Product:")
        print(product.name)

        print("\nGenerating and saving embedding...")

        saved_embedding = save_product_embedding(
            product,
            db,
        )

        print("\nEmbedding saved successfully!")
        print("Embedding ID:", saved_embedding.id)
        print("Product ID:", saved_embedding.product_id)
        print("Model:", saved_embedding.model_name)
        print(
            "Stored embedding length:",
            len(saved_embedding.embedding),
        )

finally:
    db.close()