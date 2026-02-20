from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.wojewodztwo import Wojewodztwo


class WojewodztwoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Wojewodztwo]:
        result = await self.session.execute(select(Wojewodztwo))
        return list(result.scalars().all())

    async def get(self, wojewodztwo_id: int) -> Optional[Wojewodztwo]:
        result = await self.session.execute(select(Wojewodztwo).where(Wojewodztwo.id == wojewodztwo_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, nazwa: str) -> Optional[Wojewodztwo]:
        result = await self.session.execute(select(Wojewodztwo).where(Wojewodztwo.nazwa == nazwa))
        return result.scalar_one_or_none()
