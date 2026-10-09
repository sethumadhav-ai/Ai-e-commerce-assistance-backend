import time

from app.db.session import get_db
from app.models.product import Product
from app.models.product_embedding import ProductEmbedding
from app.services.embedding_service import save_product_embedding


BATCH_SIZE = 10
DELAY_BETWEEN_PRODUCTS = 1


db = next(get_db())

try:
    products = (
        db.query(Product)
        .order_by(Product.id)
        .all()
    )

    total_products = len(products)

    print("=" * 60)
    print("PRODUCT EMBEDDING GENERATION")
    print("=" * 60)
    print(f"Total products: {total_products}")
    print()

    success_count = 0
    skipped_count = 0
    failed_count = 0

    for index, product in enumerate(products, start=1):

        existing_embedding = (
            db.query(ProductEmbedding)
            .filter(
                ProductEmbedding.product_id == product.id
            )
            .first()
        )

        if existing_embedding:
            skipped_count += 1

            print(
                f"[{index}/{total_products}] "
                f"SKIPPED - {product.name}"
            )

            continue

        print(
            f"[{index}/{total_products}] "
            f"Generating - {product.name}"
        )

        try:
            save_product_embedding(
                product,
                db,
            )

            success_count += 1

            print("    SUCCESS")

        except Exception as e:
            failed_count += 1

            print("    FAILED")
            print(f"    Error: {e}")

            # Roll back this failed database transaction
            db.rollback()

        time.sleep(DELAY_BETWEEN_PRODUCTS)

    print()
    print("=" * 60)
    print("EMBEDDING GENERATION COMPLETED")
    print("=" * 60)
    print(f"Total products : {total_products}")
    print(f"Generated      : {success_count}")
    print(f"Skipped        : {skipped_count}")
    print(f"Failed         : {failed_count}")
    print("=" * 60)

finally:
    db.close()