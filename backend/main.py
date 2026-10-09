from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.category import router as category_router
from app.api.product import router as product_router
from app.api.cart import router as cart_router
from app.api.wishlist import router as wishlist_router
from app.api.order import router as order_router
from app.api.review import router as review_router
from app.api.user_preference import router as user_preference_router
from app.api.user_product_interaction import router as interaction_router


app = FastAPI(
    title="AI E-Commerce Assistant",
    description="AI-powered e-commerce backend using Gemini",
    version="1.0.0",
)


# =========================
# Authentication Routes
# =========================

app.include_router(auth_router)


# =========================
# Category Routes
# =========================

app.include_router(category_router)




app.include_router(product_router)



app.include_router(cart_router)


app.include_router(wishlist_router)


app.include_router(order_router)

app.include_router(review_router)


app.include_router(user_preference_router)




app.include_router(interaction_router)


# =========================
# Basic Routes
# =========================

@app.get("/")
def home():
    return {
        "message": "AI E-Commerce Assistant API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }