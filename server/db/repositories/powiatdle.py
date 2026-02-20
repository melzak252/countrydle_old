from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.powiat import Powiat
from db.models.powiatdle import PowiatdleDay, PowiatdleState, PowiatdleGuess, PowiatdleQuestion
from db.models.user import User
from schemas.powiatdle import PowiatGuessCreate, PowiatQuestionCreate


class PowiatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[Powiat]:
        result = await self.session.execute(select(Powiat))
        return list(result.scalars().all())

    async def get(self, powiat_id: int) -> Optional[Powiat]:
        result = await self.session.execute(select(Powiat).where(Powiat.id == powiat_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, nazwa: str) -> Optional[Powiat]:
        result = await self.session.execute(select(Powiat).where(Powiat.nazwa == nazwa))
        return result.scalar_one_or_none()


class PowiatdleDayRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_today_powiat(self) -> Optional[PowiatdleDay]:
        today = func.current_date()
        result = await self.session.execute(
            select(PowiatdleDay).where(PowiatdleDay.date == today)
        )
        return result.scalar_one_or_none()

    async def generate_new_day_powiat(self) -> PowiatdleDay:
        # Get a random powiat
        result = await self.session.execute(select(Powiat).order_by(func.random()).limit(1))
        powiat = result.scalar_one_or_none()
        
        if not powiat:
            raise Exception("No powiaty found in database!")

        new_day = PowiatdleDay(powiat_id=powiat.id)
        self.session.add(new_day)
        await self.session.commit()
        await self.session.refresh(new_day)
        return new_day


class PowiatdleStateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self, user: User, day: PowiatdleDay) -> Optional[PowiatdleState]:
        result = await self.session.execute(
            select(PowiatdleState).where(
                and_(
                    PowiatdleState.user_id == user.id,
                    PowiatdleState.day_id == day.id
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_state(self, user: User, day: PowiatdleDay) -> PowiatdleState:
        new_state = PowiatdleState(user_id=user.id, day_id=day.id)
        self.session.add(new_state)
        await self.session.commit()
        await self.session.refresh(new_state)
        return new_state

    async def update_state(self, state: PowiatdleState) -> PowiatdleState:
        self.session.add(state)
        await self.session.commit()
        await self.session.refresh(state)
        return state


class PowiatdleGuessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_guess(self, guess_create: PowiatGuessCreate) -> PowiatdleGuess:
        new_guess = PowiatdleGuess(**guess_create.model_dump())
        self.session.add(new_guess)
        await self.session.commit()
        await self.session.refresh(new_guess)
        return new_guess

    async def get_user_day_guesses(self, user: User, day: PowiatdleDay) -> List[PowiatdleGuess]:
        result = await self.session.execute(
            select(PowiatdleGuess).where(
                and_(
                    PowiatdleGuess.user_id == user.id,
                    PowiatdleGuess.day_id == day.id
                )
            ).order_by(PowiatdleGuess.guessed_at.asc())
        )
        return list(result.scalars().all())


class PowiatdleQuestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_question(self, question_create: PowiatQuestionCreate) -> PowiatdleQuestion:
        new_question = PowiatdleQuestion(**question_create.model_dump())
        self.session.add(new_question)
        await self.session.commit()
        await self.session.refresh(new_question)
        return new_question

    async def get_user_day_questions(self, user: User, day: PowiatdleDay) -> List[PowiatdleQuestion]:
        result = await self.session.execute(
            select(PowiatdleQuestion).where(
                and_(
                    PowiatdleQuestion.user_id == user.id,
                    PowiatdleQuestion.day_id == day.id
                )
            ).order_by(PowiatdleQuestion.asked_at.asc())
        )
        return list(result.scalars().all())
