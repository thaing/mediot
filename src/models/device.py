import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class Device(Base):
    __tablename__ = "device"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    d_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("user.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="devices")
    vitals_entries: Mapped[list["Vitals"]] = relationship(
        "Vitals", back_populates="device"
    )
