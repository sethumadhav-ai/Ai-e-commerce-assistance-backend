
from app.db.session import get_db
from app.models.product import Product
from app.models.product_embedding import ProductEmbedding
from app.services.embedding_service import save_product_embedding

db = next(get_db())

try:
    product = db.get(Product, 506)
    if product is None:
        print("Product 506 was not found.")
    else:
        existing = db.query(ProductEmbedding).filter(ProductEmbedding.product_id == product.id).first()
        if existing:
            print("This product already has an embedding.")
        else:
            print("Generating embedding for:", product.name)
            saved = save_product_embedding(product, db)
            print("Embedding saved successfully!")
            print("Embedding ID:", saved.id)
            print("Product ID:", saved.product_id)
finally:
    db.close()

