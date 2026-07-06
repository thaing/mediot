from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class Vitals(Base):
    __tablename__ = "vitals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("device.id"), nullable=False, index=True
    )
    ts: Mapped[int] = mapped_column(BigInteger, nullable=False)
    hr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spo2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bp_sys: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bp_dia: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bat: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    device: Mapped["Device"] = relationship("Device", back_populates="vitals_entries")

    __table_args__ = (
        Index("ix_vitals_device_id_ts", "device_id", "ts"),
    )