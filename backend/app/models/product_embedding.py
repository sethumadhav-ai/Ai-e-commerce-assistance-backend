
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Preserve existing JSON embeddings.
    embedding: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # New pgvector column for 3072-dimensional embeddings.
    embedding_vector: Mapped[list[float] | None] = mapped_column(
        Vector(3072),
        nullable=True,
    )

    model_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
