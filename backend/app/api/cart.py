from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
)


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


def get_or_create_cart(
    user: User,
    db: Session,
) -> Cart:
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == user.id)
        .first()
    )

    if cart is None:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


def build_cart_response(
    cart: Cart,
    db: Session,
) -> CartResponse:

    cart_items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )

    response_items = []
    total_items = 0
    total_price = 0.0

    for item in cart_items:

        product = db.get(
            Product,
            item.product_id,
        )

        if product is None:
            continue

        subtotal = product.price * item.quantity

        response_items.append(
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name,
                "quantity": item.quantity,
                "unit_price": product.price,
                "subtotal": subtotal,
            }
        )

        total_items += item.quantity
        total_price += subtotal

    return CartResponse(
        id=cart.id,
        items=response_items,
        total_items=total_items,
        total_price=round(total_price, 2),
    )


@router.get(
    "/",
    response_model=CartResponse,
)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = get_or_create_cart(
        current_user,
        db,
    )

    return build_cart_response(
        cart,
        db,
    )


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(
        Product,
        item_data.product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not active",
        )

    if product.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is out of stock",
        )

    cart = get_or_create_cart(
        current_user,
        db,
    )

    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item_data.product_id,
        )
        .first()
    )

    if existing_item:

        new_quantity = (
            existing_item.quantity
            + item_data.quantity
        )

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.stock} units are available",
            )

        existing_item.quantity = new_quantity

    else:

        if item_data.quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.stock} units are available",
            )

        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )

        db.add(new_item)

    db.commit()

    return build_cart_response(
        cart,
        db,
    )


@router.put(
    "/items/{item_id}",
    response_model=CartResponse,
)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
        .first()
    )

    if cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    product = db.get(
        Product,
        cart_item.product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if item_data.quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.stock} units are available",
        )

    cart_item.quantity = item_data.quantity

    db.commit()

    return build_cart_response(
        cart,
        db,
    )


@router.delete(
    "/items/{item_id}",
    response_model=CartResponse,
)
def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
        .first()
    )

    if cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    db.delete(cart_item)
    db.commit()

    return build_cart_response(
        cart,
        db,
    )


@router.delete(
    "/",
    response_model=CartResponse,
)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id)
        .first()
    )

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .delete()
    )

    db.commit()

    return build_cart_response(
        cart,
        db,
    )