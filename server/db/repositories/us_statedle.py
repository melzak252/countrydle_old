from typing import List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.us_state import USState
from db.models.us_statedle import USStatedleDay, USStatedleState, USStatedleGuess, USStatedleQuestion
from db.models.user import User
from schemas.us_statedle import USStateGuessCreate, USStateQuestionCreate


class USStatedleDayRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_today_us_state(self) -> Optional[USStatedleDay]:
        today = func.current_date()
        result = await self.session.execute(
            select(USStatedleDay).where(USStatedleDay.date == today)
        )
        return result.scalar_one_or_none()

    async def generate_new_day_us_state(self) -> USStatedleDay:
        # Get a random us_state
        result = await self.session.execute(select(USState).order_by(func.random()).limit(1))
        us_state = result.scalar_one_or_none()
        
        if not us_state:
            raise Exception("No US states found in database!")

        new_day = USStatedleDay(us_state_id=us_state.id)
        self.session.add(new_day)
        await self.session.commit()
        await self.session.refresh(new_day)
        return new_day


class USStatedleStateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self, user: User, day: USStatedleDay) -> Optional[USStatedleState]:
        result = await self.session.execute(
            select(USStatedleState).where(
                and_(
                    USStatedleState.user_id == user.id,
                    USStatedleState.day_id == day.id
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_state(self, user: User, day: USStatedleDay) -> USStatedleState:
        new_state = USStatedleState(user_id=user.id, day_id=day.id)
        self.session.add(new_state)
        await self.session.commit()
        await self.session.refresh(new_state)
        return new_state

    async def update_state(self, state: USStatedleState) -> USStatedleState:
        self.session.add(state)
        await self.session.commit()
        await self.session.refresh(state)
        return state


class USStatedleGuessRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_guess(self, guess_create: USStateGuessCreate) -> USStatedleGuess:
        new_guess = USStatedleGuess(**guess_create.model_dump())
        self.session.add(new_guess)
        await self.session.commit()
        await self.session.refresh(new_guess)
        return new_guess

    async def get_user_day_guesses(self, user: User, day: USStatedleDay) -> List[USStatedleGuess]:
        result = await self.session.execute(
            select(USStatedleGuess).where(
                and_(
                    USStatedleGuess.user_id == user.id,
                    USStatedleGuess.day_id == day.id
                )
            ).order_by(USStatedleGuess.guessed_at.asc())
        )
        return list(result.scalars().all())


class USStatedleQuestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_question(self, question_create: USStateQuestionCreate) -> USStatedleQuestion:
        new_question = USStatedleQuestion(**question_create.model_dump())
        self.session.add(new_question)
        await self.session.commit()
        await self.session.refresh(new_question)
        return new_question

    async def get_user_day_questions(self, user: User, day: USStatedleDay) -> List[USStatedleQuestion]:
        result = await self.session.execute(
            select(USStatedleQuestion).where(
                and_(
                    USStatedleQuestion.user_id == user.id,
                    USStatedleQuestion.day_id == day.id
                )
            ).order_by(USStatedleQuestion.asked_at.asc())
        )
        return list(result.scalars().all())
