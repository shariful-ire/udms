from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, RefreshToken
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username.lower())
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalars().first()

    async def get_by_student_id(self, student_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.student_id == student_id)
        )
        return result.scalars().first()

    async def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Look up user by username OR email."""
        norm = identifier.lower().strip()
        result = await self.db.execute(
            select(User).where(or_(User.username == norm, User.email == norm))
        )
        return result.scalars().first()

    async def get_paginated(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[User], int]:
        query = select(User)
        count_query = select(func.count()).select_from(User)

        conditions = []
        if search:
            pattern = f"%{search}%"
            conditions.append(
                or_(
                    User.username.ilike(pattern),
                    User.full_name.ilike(pattern),
                    User.email.ilike(pattern),
                    User.student_id.ilike(pattern),
                )
            )
        if role:
            conditions.append(User.role == role)
        if status:
            conditions.append(User.status == status)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * per_page
        items = (
            await self.db.execute(
                query.order_by(User.created_at.desc()).offset(offset).limit(per_page)
            )
        ).scalars().all()

        return list(items), total

    async def has_active_dining_manager(self) -> bool:
        result = await self.db.execute(
            select(func.count()).where(
                and_(User.role == "DINING_MANAGER", User.status == "ACTIVE")
            )
        )
        return (result.scalar() or 0) > 0

    async def get_active_dining_manager(self) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(
                and_(User.role == "DINING_MANAGER", User.status == "ACTIVE")
            )
        )
        return result.scalars().first()

    async def increment_failed_attempts(self, user_id: str) -> int:
        result = await self.db.execute(
            select(User.failed_attempts).where(User.id == user_id)
        )
        current = result.scalar() or 0
        new_count = current + 1
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(failed_attempts=new_count)
        )
        return new_count

    async def reset_failed_attempts(self, user_id: str) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(failed_attempts=0, locked_until=None)
        )

    async def lock_account(self, user_id: str, locked_until: datetime) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(locked_until=locked_until)
        )

    async def update_last_login(self, user_id: str) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.now(timezone.utc))
        )

    async def count_by_role(self) -> dict:
        result = await self.db.execute(
            select(User.role, func.count(User.id)).group_by(User.role)
        )
        return {row[0]: row[1] for row in result.all()}

    async def count_by_status(self) -> dict:
        result = await self.db.execute(
            select(User.status, func.count(User.id)).group_by(User.status)
        )
        return {row[0]: row[1] for row in result.all()}

    async def get_recent(self, limit: int = 5) -> List[User]:
        result = await self.db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalars().first()

    async def delete_by_user_id(self, user_id: str) -> int:
        """Delete all refresh tokens for a user (logout all sessions)."""
        from sqlalchemy import delete
        result = await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return result.rowcount

    async def delete_expired(self) -> int:
        """Cleanup expired tokens."""
        from sqlalchemy import delete
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < now)
        )
        return result.rowcount
