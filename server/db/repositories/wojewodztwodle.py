from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.wojewodztwo import Wojewodztwo
from db.models.wojewodztwodle import WojewodztwodleDay, WojewodztwodleState, WojewodztwodleGuess, WojewodztwodleQuestion
from db.models.user import User
from schemas.wojewodztwodle import WojewodztwoGuessCreate, WojewodztwoQuestionCreate


class WojewodztwodleDayRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_today_wojewodztwo(self) -> Optional[WojewodztwodleDay]:
        today = func.current_date()
        result = await self.session.execute(
            select(WojewodztwodleDay).where(WojewodztwodleDay.date == today)
        )
        return result.scalar_one_or_none()

    async def generate_new_day_wojewodztwo(self) -> WojewodztwodleDay:
        # Get a random wojewodztwo
        result = await self.session.execute(select(Wojewodztwo).order_by(func.random()).limit(1))
        wojewodztwo = result.scalar_one_or_none()
        
        if not wojewodztwo:
            raise Exception("No wojewodztwa found in database!")

        new_day = WojewodztwodleDay(wojewodztwo_id=wojewodztwo.id)
        self.session.add(new_day)
        await self.session.commit()
        await self.session.refresh(new_day)
        return new_day


class WojewodztwodleStateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self, user: User, day: WojewodztwodleDay) -> Optional[WojewodztwodleState]:
        result = await self.session.execute(
            select(WojewodztwodleState).where(
                and_(
                    WojewodztwodleState.user_id == user.id,
                    WojewodztwodleState.day_id == day.id
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_state(self, user: User, day: WojewodztwodleDay) -> WojewodztwodleState:
        new_state = WojewodztwodleState(user_id=user.id, day_id=day.id)
        self.session.add(new_state)
        await self.session.commit()
        await self.session.refresh(new_state)
        return new_state

    async def update_state(self, state: WojewodztwodleState) -> WojewodztwodleState:
        self.session.add(state)
        await self.session.commit()
        await self.session.refresh(state)
        return state


class WojewodztwodleGuessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_guess(self, guess_create: WojewodztwoGuessCreate) -> WojewodztwodleGuess:
        new_guess = WojewodztwodleGuess(**guess_create.model_dump())
        self.session.add(new_guess)
        await self.session.commit()
        await self.session.refresh(new_guess)
        return new_guess

    async def get_user_day_guesses(self, user: User, day: WojewodztwodleDay) -> List[WojewodztwodleGuess]:
        result = await self.session.execute(
            select(WojewodztwodleGuess).where(
                and_(
                    WojewodztwodleGuess.user_id == user.id,
                    WojewodztwodleGuess.day_id == day.id
                )
            ).order_by(WojewodztwodleGuess.guessed_at.asc())
        )
        return list(result.scalars().all())


class WojewodztwodleQuestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_question(self, question_create: WojewodztwoQuestionCreate) -> WojewodztwodleQuestion:
        new_question = WojewodztwodleQuestion(**question_create.model_dump())
        self.session.add(new_question)
        await self.session.commit()
        await self.session.refresh(new_question)
        return new_question

    async def get_user_day_questions(self, user: User, day: WojewodztwodleDay) -> List[WojewodztwodleQuestion]:
        result = await self.session.execute(
            select(WojewodztwodleQuestion).where(
                and_(
                    WojewodztwodleQuestion.user_id == user.id,
                    WojewodztwodleQuestion.day_id == day.id
                )
            ).order_by(WojewodztwodleQuestion.asked_at.asc())
        )
        return list(result.scalars().all())
