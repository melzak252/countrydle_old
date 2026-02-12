from typing import List
from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import DayCountry, Guess, User
from schemas.countrydle import (
    GuessCreate,
)


class GuessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, gid: int) -> Guess:
        result = await self.session.execute(select(Guess).where(Guess.id == gid))

        return result.scalars().first()

    async def add_guess(self, guess: GuessCreate) -> Guess:
        new_entry = Guess(**guess.model_dump(exclude={"country_id"}))

        self.session.add(new_entry)

        try:
            await self.session.commit()  # Commit the transaction
            await self.session.refresh(new_entry)  # Refresh the instance to get the ID
        except Exception as ex:
            await self.session.rollback()
            raise ex

        return new_entry

    async def get_user_day_guesses(self, user: User, day: DayCountry) -> List[Guess]:
        questions_result = await self.session.execute(
            select(Guess).where(Guess.user_id == user.id, Guess.day_id == day.id)
        )

        return questions_result.scalars().all()

    async def get_user_guess_statistics(self, user: User) -> List[Guess]:
        questions_result = await self.session.execute(
            select(
                func.count(Guess.id).label("count"),
                func.sum(Guess.answer.cast(Integer)).label("correct"),
                func.sum((Guess.answer == False).cast(Integer)).label("incorrect"),
            ).where(Guess.user_id == user.id)
        )
        row = questions_result.first()
        return row
