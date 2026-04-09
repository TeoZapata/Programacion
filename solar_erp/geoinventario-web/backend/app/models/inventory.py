from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class MovementType(StrEnum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    sku: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    unit: Mapped[str] = mapped_column(String(50), default="unidad")
    stock: Mapped[int] = mapped_column(Integer, default=0)
    minimum_stock: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    movements: Mapped[list["InventoryMovement"]] = relationship(back_populates="material")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    movement_type: Mapped[MovementType] = mapped_column(Enum(MovementType))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_cost: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    material: Mapped[Material] = relationship(back_populates="movements")
