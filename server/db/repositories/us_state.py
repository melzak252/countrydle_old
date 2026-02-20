from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.us_state import USState


class USStateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[USState]:
        result = await self.session.execute(select(USState))
        return list(result.scalars().all())

    async def get(self, state_id: int) -> Optional[USState]:
        result = await self.session.execute(select(USState).where(USState.id == state_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[USState]:
        result = await self.session.execute(select(USState).where(USState.name == name))
        return result.scalar_one_or_none()
