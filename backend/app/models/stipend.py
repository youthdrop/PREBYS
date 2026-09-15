from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class YouthStipend(Base):
    __tablename__ = "youth_stipends"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    youth_id: Mapped[int] = mapped_column(
        ForeignKey("youth.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    session_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    curriculum_session: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    attendance_status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        default=50.00,
        nullable=False,
    )

    payment_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    payment_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    created_by_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )