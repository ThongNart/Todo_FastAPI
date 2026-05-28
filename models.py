from __future__ import annotations

from datetime import datetime, UTC

from sqlalchemy import DateTime, Integer, String, Boolean, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base



class TodoItem(Base):
    __tablename__ = "todo_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    urgency_level: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(UTC)
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
                                                 
    @property
    def is_overdue(self) -> bool:
        # Example logic: consider overdue if created more than 7 days ago
        return (datetime.now(UTC) - self.created_at).days > 7