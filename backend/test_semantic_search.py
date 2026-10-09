
from sqlalchemy.orm import Session

from database import engine
from app.services.semantic_search_service import search_similar_products


def main():
    db = Session(bind=engine)

    try:
        results = search_similar_products(
            "wireless headphones for travelling",
            db,
            limit=5,
        )

        print(f"Results found: {len(results)}")
        print("-" * 60)

        for product in results:
            print("Name:", product["name"])
            print("Brand:", product["brand"])
            print("Price:", product["price"])
            print("Similarity:", product["similarity"])
            print("-" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()