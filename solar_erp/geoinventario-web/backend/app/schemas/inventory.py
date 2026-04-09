from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.inventory import MovementType
from app.models.user import UserRole


class MaterialCreate(BaseModel):
    name: str
    sku: str
    unit: str = "unidad"
    minimum_stock: int = 0
    description: str | None = None


class MaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    unit: str
    stock: int
    minimum_stock: int
    description: str | None
    created_at: datetime


class MovementCreate(BaseModel):
    material_id: int
    movement_type: MovementType
    quantity: int = Field(gt=0)
    unit_cost: float | None = None
    note: str | None = None


class MovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    user_id: int
    movement_type: MovementType
    quantity: int
    unit_cost: float | None
    note: str | None
    created_at: datetime


class InventorySummary(BaseModel):
    total_materials: int
    low_stock_materials: int
    total_stock_units: int


class PermissionSummary(BaseModel):
    role: UserRole
    can_manage_inventory: bool
    can_record_movements: bool
    can_manage_users: bool
