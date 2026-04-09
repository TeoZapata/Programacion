from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryMovement, Material, MovementType


class MaterialRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Material]:
        statement = select(Material).order_by(Material.name.asc())
        return list(self.session.scalars(statement))

    def get_by_id(self, material_id: int) -> Material | None:
        statement = select(Material).where(Material.id == material_id)
        return self.session.scalar(statement)

    def get_by_sku(self, sku: str) -> Material | None:
        statement = select(Material).where(Material.sku == sku)
        return self.session.scalar(statement)

    def create(
        self,
        *,
        name: str,
        sku: str,
        unit: str,
        minimum_stock: int,
        description: str | None,
    ) -> Material:
        material = Material(
            name=name,
            sku=sku,
            unit=unit,
            minimum_stock=minimum_stock,
            description=description,
        )
        self.session.add(material)
        self.session.commit()
        self.session.refresh(material)
        return material


class MovementRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[InventoryMovement]:
        statement = select(InventoryMovement).order_by(InventoryMovement.created_at.desc())
        return list(self.session.scalars(statement))

    def create(
        self,
        *,
        material: Material,
        user_id: int,
        movement_type: MovementType,
        quantity: int,
        unit_cost: float | None,
        note: str | None,
    ) -> InventoryMovement:
        if movement_type == MovementType.OUT and material.stock < quantity:
            raise ValueError("Insufficient stock for this movement")

        if movement_type == MovementType.IN:
            material.stock += quantity
        elif movement_type == MovementType.OUT:
            material.stock -= quantity
        else:
            material.stock = quantity

        movement = InventoryMovement(
            material_id=material.id,
            user_id=user_id,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=unit_cost,
            note=note,
        )
        self.session.add(movement)
        self.session.add(material)
        self.session.commit()
        self.session.refresh(movement)
        return movement
