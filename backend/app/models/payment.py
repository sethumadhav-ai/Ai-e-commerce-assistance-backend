from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )

    payment_provider: Mapped[str] = mapped_column(
        String(50),
        default="stripe",
        nullable=False
    )

    payment_intent_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )