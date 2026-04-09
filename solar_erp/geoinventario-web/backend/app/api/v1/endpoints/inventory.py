from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session, require_roles
from app.models.inventory import MovementType
from app.models.user import User, UserRole
from app.repositories.inventory import MaterialRepository, MovementRepository
from app.schemas.inventory import (
    InventorySummary,
    MaterialCreate,
    MaterialRead,
    MovementCreate,
    MovementRead,
    PermissionSummary,
)

router = APIRouter()


@router.get("/permissions", response_model=PermissionSummary)
def get_permissions(current_user: User = Depends(get_current_user)) -> PermissionSummary:
    role = current_user.role
    return PermissionSummary(
        role=role,
        can_manage_inventory=role in {UserRole.ADMIN, UserRole.MANAGER},
        can_record_movements=role in {UserRole.ADMIN, UserRole.MANAGER, UserRole.OPERATOR},
        can_manage_users=role == UserRole.ADMIN,
    )


@router.get("/materials", response_model=list[MaterialRead])
def list_materials(
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[MaterialRead]:
    materials = MaterialRepository(session).list_all()
    return [MaterialRead.model_validate(material) for material in materials]


@router.post(
    "/materials",
    response_model=MaterialRead,
    status_code=status.HTTP_201_CREATED,
)
def create_material(
    payload: MaterialCreate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
) -> MaterialRead:
    repository = MaterialRepository(session)
    if repository.get_by_sku(payload.sku) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")

    material = repository.create(
        name=payload.name,
        sku=payload.sku,
        unit=payload.unit,
        minimum_stock=payload.minimum_stock,
        description=payload.description,
    )
    return MaterialRead.model_validate(material)


@router.get("/movements", response_model=list[MovementRead])
def list_movements(
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[MovementRead]:
    movements = MovementRepository(session).list_all()
    return [MovementRead.model_validate(movement) for movement in movements]


@router.post(
    "/movements",
    response_model=MovementRead,
    status_code=status.HTTP_201_CREATED,
)
def create_movement(
    payload: MovementCreate,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.OPERATOR)),
) -> MovementRead:
    material_repository = MaterialRepository(session)
    material = material_repository.get_by_id(payload.material_id)
    if material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")

    try:
        movement = MovementRepository(session).create(
            material=material,
            user_id=current_user.id,
            movement_type=payload.movement_type,
            quantity=payload.quantity,
            unit_cost=payload.unit_cost,
            note=payload.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return MovementRead.model_validate(movement)


@router.get("/summary", response_model=InventorySummary)
def get_inventory_summary(
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> InventorySummary:
    materials = MaterialRepository(session).list_all()
    return InventorySummary(
        total_materials=len(materials),
        low_stock_materials=sum(1 for material in materials if material.stock <= material.minimum_stock),
        total_stock_units=sum(material.stock for material in materials),
    )
