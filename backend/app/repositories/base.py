from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async CRUD repository for SQLAlchemy models."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: Dict[str, Any] = None,
    ) -> Tuple[List[ModelType], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))

        total = (await self.db.execute(count_query)).scalar() or 0
        items = (
            await self.db.execute(query.offset(skip).limit(limit))
        ).scalars().all()

        return list(items), total

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            if value is not None or field in obj_in:
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> bool:
        await self.db.delete(db_obj)
        await self.db.flush()
        return True

    async def count(self, filters: Dict[str, Any] = None) -> int:
        query = select(func.count()).select_from(self.model)
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
            if conditions:
                query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar() or 0
