from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("ai_conversations.id"),
        nullable=False,
        index=True
    )

    role: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )