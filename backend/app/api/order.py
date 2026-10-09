from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db

from app.models.user import User
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem

from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Find the user's cart
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 2. Get cart items
    # ---------------------------------------------------------

    cart_items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create order because cart is empty",
        )

    # ---------------------------------------------------------
    # 3. Validate products and calculate total
    # ---------------------------------------------------------

    order_items_data = []
    total_amount = 0.0

    for cart_item in cart_items:

        product = db.get(
            Product,
            cart_item.product_id,
        )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {cart_item.product_id} not found",
            )

        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is no longer available",
            )

        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Only {product.stock} units of "
                    f"'{product.name}' are available"
                ),
            )

        unit_price = float(product.price)

        subtotal = unit_price * cart_item.quantity

        total_amount += subtotal

        order_items_data.append(
            {
                "product": product,
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            }
        )

    # ---------------------------------------------------------
    # 4. Create the order
    # ---------------------------------------------------------

    new_order = Order(
        user_id=current_user.id,
        status="pending",
        payment_status="pending",
        total_amount=round(total_amount, 2),
        shipping_address=order_data.shipping_address,
    )

    db.add(new_order)

    # Get the generated order ID
    db.flush()

    # ---------------------------------------------------------
    # 5. Create order items and reduce stock
    # ---------------------------------------------------------

    for item_data in order_items_data:

        product = item_data["product"]

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            subtotal=round(item_data["subtotal"], 2),
        )

        db.add(order_item)

        # Reduce stock
        product.stock -= item_data["quantity"]

    # ---------------------------------------------------------
    # 6. Clear the cart
    # ---------------------------------------------------------

    for cart_item in cart_items:
        db.delete(cart_item)

    # ---------------------------------------------------------
    # 7. Save transaction
    # ---------------------------------------------------------

    db.commit()

    db.refresh(new_order)

    # ---------------------------------------------------------
    # 8. Get saved order items
    # ---------------------------------------------------------

    saved_order_items = (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == new_order.id
        )
        .all()
    )

    response_items = []

    for order_item in saved_order_items:

        product = db.get(
            Product,
            order_item.product_id,
        )

        response_items.append(
            {
                "id": order_item.id,
                "product_id": order_item.product_id,
                "product_name": (
                    product.name
                    if product
                    else "Unknown Product"
                ),
                "quantity": order_item.quantity,
                "unit_price": order_item.unit_price,
                "subtotal": order_item.subtotal,
            }
        )

    # ---------------------------------------------------------
    # 9. Return order
    # ---------------------------------------------------------

    return {
        "id": new_order.id,
        "total_amount": float(new_order.total_amount),
        "status": new_order.status,
        "payment_status": new_order.payment_status,
        "shipping_address": new_order.shipping_address,
        "created_at": new_order.created_at,
        "items": response_items,
    }


@router.get(
    "/",
    response_model=list[OrderListResponse],
)
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Get only the current user's orders
    # ---------------------------------------------------------

    orders = (
        db.query(Order)
        .filter(
            Order.user_id == current_user.id
        )
        .order_by(Order.id.desc())
        .all()
    )

    response = []

    for order in orders:

        total_items = (
            db.query(OrderItem)
            .filter(
                OrderItem.order_id == order.id
            )
            .count()
        )

        response.append(
            {
                "id": order.id,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "payment_status": order.payment_status,
                "shipping_address": order.shipping_address,
                "created_at": order.created_at,
                "total_items": total_items,
            }
        )

    return response


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Find only the current user's order
    # ---------------------------------------------------------

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # ---------------------------------------------------------
    # Get order items
    # ---------------------------------------------------------

    order_items = (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id == order.id
        )
        .all()
    )

    response_items = []

    for order_item in order_items:

        product = db.get(
            Product,
            order_item.product_id,
        )

        response_items.append(
            {
                "id": order_item.id,
                "product_id": order_item.product_id,
                "product_name": (
                    product.name
                    if product
                    else "Unknown Product"
                ),
                "quantity": order_item.quantity,
                "unit_price": order_item.unit_price,
                "subtotal": order_item.subtotal,
            }
        )

    return {
        "id": order.id,
        "total_amount": float(order.total_amount),
        "status": order.status,
        "payment_status": order.payment_status,
        "shipping_address": order.shipping_address,
        "created_at": order.created_at,
        "items": response_items,
    }