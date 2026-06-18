from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, get_db, get_redis
from app.core.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    RoleChangeNotAllowedException,
)
from app.core.permissions import Permission, UserRole, require_permission, require_roles
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.common import APIResponse, paginate
from app.schemas.user import UserAdminUpdate, UserCreate, UserResponse, UserStatsResponse, UserSummary
from app.core.security import hash_password
from app.repositories.meal_repo import AuditRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all users (Provost only)."""
    repo = UserRepository(db)
    users, total = await repo.get_paginated(
        page=page, per_page=per_page, search=search, role=role, status=status
    )
    return {
        "success": True,
        "data": [UserResponse.model_validate(u) for u in users],
        "meta": paginate(page, per_page, total).__dict__,
    }


@router.get("/stats", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def get_user_stats(db: AsyncSession = Depends(get_db)):
    """User statistics for Provost dashboard."""
    repo = UserRepository(db)
    by_role = await repo.count_by_role()
    by_status = await repo.count_by_status()
    return {
        "success": True,
        "data": {
            "total_users": sum(by_role.values()),
            "total_customers": by_role.get("CUSTOMER", 0),
            "total_non_customers": by_role.get("NON_CUSTOMER", 0),
            "total_managers": by_role.get("DINING_MANAGER", 0),
            "active_users": by_status.get("ACTIVE", 0),
            "inactive_users": by_status.get("INACTIVE", 0),
            "suspended_users": by_status.get("SUSPENDED", 0),
        },
    }


@router.get("/recent", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def get_recent_users(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    users = await repo.get_recent(limit)
    return {"success": True, "data": [UserSummary.model_validate(u) for u in users]}


@router.post("", status_code=201, dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def create_user(
    data: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Admin user creation (Provost only)."""
    from app.core.exceptions import ConflictException
    repo = UserRepository(db)

    if await repo.get_by_username(data.username):
        raise ConflictException("Username already taken")
    if await repo.get_by_email(data.email):
        raise ConflictException("Email already registered")
    if await repo.get_by_student_id(data.student_id):
        raise ConflictException("Student ID already registered")

    user = await repo.create({
        "username": data.username.lower(),
        "email": data.email.lower(),
        "full_name": data.full_name,
        "password_hash": hash_password(data.password),
        "student_id": data.student_id,
        "department": data.department,
        "batch": data.batch,
        "hall_name": data.hall_name,
        "phone": data.phone,
        "role": data.role,
        "status": "ACTIVE",
        "email_verified": True,
    })

    audit = AuditRepository(db)
    await audit.log(
        user_id=current_user.id,
        action="USER_CREATED",
        entity_type="User",
        entity_id=user.id,
        new_value={"username": user.username, "role": user.role},
    )

    return {"success": True, "message": "User created", "data": UserResponse.model_validate(user)}


@router.get("/{user_id}", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User", user_id)
    return {"success": True, "data": UserResponse.model_validate(user)}


@router.put("/{user_id}", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def update_user(
    user_id: str,
    data: UserAdminUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User", user_id)
    if user.role == "PROVOST":
        raise RoleChangeNotAllowedException()

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = await repo.update(user, update_data)
    return {"success": True, "data": UserResponse.model_validate(updated)}


@router.delete("/{user_id}", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User", user_id)
    if user.role == "PROVOST":
        raise PermissionDeniedException("Cannot delete the Provost account")
    if user.id == current_user.id:
        raise PermissionDeniedException("Cannot delete your own account")

    audit = AuditRepository(db)
    await audit.log(
        user_id=current_user.id,
        action="USER_DELETED",
        entity_type="User",
        entity_id=user.id,
        old_value={"username": user.username},
    )
    await repo.delete(user)
    return {"success": True, "message": "User deleted"}


@router.patch("/{user_id}/suspend", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def suspend_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User", user_id)
    if user.role == "PROVOST":
        raise PermissionDeniedException("Cannot suspend the Provost")
    await repo.update(user, {"status": "SUSPENDED"})
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="USER_SUSPENDED", entity_type="User", entity_id=user_id)
    return {"success": True, "message": "User suspended"}


@router.patch("/{user_id}/activate", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def activate_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User", user_id)
    await repo.update(user, {"status": "ACTIVE"})
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="USER_ACTIVATED", entity_type="User", entity_id=user_id)
    return {"success": True, "message": "User activated"}


@router.patch("/{user_id}/assign-manager", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def assign_manager(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User", user_id)
    if user.role == "PROVOST":
        raise RoleChangeNotAllowedException()

    old_role = user.role
    await repo.update(user, {"role": "DINING_MANAGER"})
    audit = AuditRepository(db)
    await audit.log(
        user_id=current_user.id,
        action="MANAGER_ASSIGNED",
        entity_type="User",
        entity_id=user_id,
        old_value={"role": old_role},
        new_value={"role": "DINING_MANAGER"},
    )
    return {"success": True, "message": f"{user.full_name} is now a Dining Manager"}


@router.patch("/{user_id}/remove-manager", dependencies=[Depends(require_roles(UserRole.PROVOST))])
async def remove_manager(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundException("User", user_id)
    if user.role != "DINING_MANAGER":
        from app.core.exceptions import ValidationException
        raise ValidationException("User is not a Dining Manager")

    await repo.update(user, {"role": "NON_CUSTOMER"})
    audit = AuditRepository(db)
    await audit.log(
        user_id=current_user.id,
        action="MANAGER_REMOVED",
        entity_type="User",
        entity_id=user_id,
        old_value={"role": "DINING_MANAGER"},
        new_value={"role": "NON_CUSTOMER"},
    )
    return {"success": True, "message": f"{user.full_name}'s manager role has been removed"}
