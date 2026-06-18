from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, get_db
from app.core.exceptions import InvalidFileTypeException, UploadTooLargeException
from app.core.config import settings
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import ChangePasswordRequest, UserResponse, UserUpdate
from app.core.security import hash_password, verify_password
from app.core.exceptions import InvalidCredentialsException

profile_router = APIRouter(prefix="/profile", tags=["Profile"])
settings_router = APIRouter(prefix="/settings", tags=["Settings"])


@profile_router.get("")
async def get_profile(current_user: User = Depends(get_current_active_user)):
    return {"success": True, "data": UserResponse.model_validate(current_user)}


@profile_router.put("")
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = await repo.update(current_user, update_data)
    return {"success": True, "data": UserResponse.model_validate(updated)}


@profile_router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise InvalidCredentialsException("Current password is incorrect")

    repo = UserRepository(db)
    await repo.update(current_user, {"password_hash": hash_password(data.new_password)})
    return {"success": True, "message": "Password changed successfully"}


@profile_router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise InvalidFileTypeException(settings.ALLOWED_IMAGE_TYPES)

    # Read and validate size
    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise UploadTooLargeException(settings.MAX_UPLOAD_SIZE_MB)

    # Save file
    import os
    import uuid
    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    upload_path = os.path.join(settings.UPLOAD_DIR, "avatars", filename)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)

    with open(upload_path, "wb") as f:
        f.write(contents)

    repo = UserRepository(db)
    url = f"/uploads/avatars/{filename}"
    updated = await repo.update(current_user, {"profile_image": url})
    return {"success": True, "data": {"profile_image": url}}


@settings_router.get("")
async def get_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.expense import SystemSetting
    r = await db.execute(select(SystemSetting))
    rows = r.scalars().all()
    return {"success": True, "data": {row.key_name: row.value for row in rows}}


@settings_router.put("")
async def update_settings(
    updates: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.permissions import UserRole
    if current_user.role != UserRole.PROVOST.value:
        from app.core.exceptions import PermissionDeniedException
        raise PermissionDeniedException("Only Provost can modify settings")

    from sqlalchemy import select
    from app.models.expense import SystemSetting
    for key, value in updates.items():
        r = await db.execute(select(SystemSetting).where(SystemSetting.key_name == key))
        setting = r.scalars().first()
        if setting:
            setting.value = str(value)
            setting.updated_by = current_user.id
            db.add(setting)
        else:
            db.add(SystemSetting(key_name=key, value=str(value), updated_by=current_user.id))

    from app.repositories.meal_repo import AuditRepository
    audit = AuditRepository(db)
    await audit.log(user_id=current_user.id, action="SETTINGS_UPDATED", entity_type="SystemSetting", new_value=updates)
    return {"success": True, "message": "Settings updated"}
