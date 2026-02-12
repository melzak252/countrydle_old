from typing import Union

from db import get_db
from db.models import User
from db.repositories.countrydle import CountrydleRepository, CountrydleStateRepository
from schemas.countrydle import (
    CountrydleEndStateResponse,
    CountrydleEndStateSchema,
    CountrydleStateResponse,
    CountrydleStateSchema,
    FullUserHistory,
    GuessBase,
    GuessCreate,
    GuessDisplay,
    InvalidQuestionDisplay,
    QuestionBase,
    QuestionCreate,
    QuestionDisplay,
)
from schemas.country import CountryDisplay
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from countrydle import statistics
from db.repositories.guess import GuessRepository
from db.repositories.question import QuestionsRepository
from qdrant.utils import add_question_to_qdrant
from db.repositories.country import CountryRepository
from users.utils import get_current_user

import countrydle.utils as gutils

load_dotenv()

router = APIRouter(prefix="/countrydle")

router.include_router(statistics.router)


@router.get("/state", response_model=CountrydleStateResponse)
async def get_state(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    day_country = await CountrydleRepository(session).get_today_country()
    state = await CountrydleStateRepository(session).get_state(user, day_country)
    guesses = await GuessRepository(session).get_user_day_guesses(user, day_country)
    questions = await QuestionsRepository(session).get_user_day_questions(
        user, day_country
    )

    if state is None:
        return await CountrydleStateRepository(session).add_countrydle_state(
            user, day_country
        )

    questions = [
        (
            QuestionDisplay.model_validate(question)
            if question.valid
            else InvalidQuestionDisplay.model_validate(question)
        )
        for question in questions
    ]

    response_state = CountrydleStateSchema.model_validate(state)

    return CountrydleStateResponse(
        user=user,
        date=str(day_country.date),
        state=response_state,
        guesses=guesses,
        questions=questions,
    )


@router.get("/end/state", response_model=CountrydleEndStateResponse)
async def get_end_state(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    day_country = await CountrydleRepository(session).get_today_country()
    state = await CountrydleStateRepository(session).get_state(user, day_country)
    guesses = await GuessRepository(session).get_user_day_guesses(user, day_country)
    questions = await QuestionsRepository(session).get_user_day_questions(
        user, day_country
    )

    if not state.is_game_over:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The player is still playing the game!",
        )

    country = await CountryRepository(session).get(day_country.country_id)
    return CountrydleEndStateResponse(
        user=user,
        date=str(day_country.date),
        country=country,
        state=CountrydleEndStateSchema.model_validate(state),
        guesses=guesses,
        questions=questions,
    )


@router.get("/countries", response_model=list[CountryDisplay])
async def get_countries(
    session: AsyncSession = Depends(get_db),
):
    return await CountryRepository(session).get_all_countries()


@router.post("/guess", response_model=GuessDisplay)
async def get_game(
    guess: GuessBase,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    daily_country = await CountrydleRepository(session).get_today_country()
    state = await CountrydleStateRepository(session).get_player_countrydle_state(
        user, daily_country
    )
    if not state.remaining_guesses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no more guesses left!",
        )

    if state.is_game_over:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User finished the game already!",
        )

    if guess.country_id:
        answer = guess.country_id == daily_country.country_id
    else:
        # Fallback to old logic if country_id is not provided (optional)
        answer_dict = await gutils.give_guess(
            guess=guess.guess, daily_country=daily_country, user=user, session=session
        )
        answer: bool = answer_dict["answer"]

    guess_create = GuessCreate(
        guess=guess.guess,
        day_id=daily_country.id,
        user_id=user.id,
        answer=answer,
    )
    guess = await GuessRepository(session).add_guess(guess_create)
    state = await CountrydleStateRepository(session).guess_made(state, guess)
    return guess


@router.post("/question", response_model=QuestionDisplay | InvalidQuestionDisplay)
async def ask_question(
    question: QuestionBase,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    day_country = await CountrydleRepository(session).get_today_country()
    state = await CountrydleStateRepository(session).get_player_countrydle_state(
        user, day_country
    )

    if state.is_game_over:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User finished the game already!",
        )

    if not state.remaining_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no more questions left!",
        )

    enh_question = await gutils.enhance_question(question.question)
    if not enh_question.valid:
        question_create = QuestionCreate(
            user_id=user.id,
            day_id=day_country.id,
            original_question=enh_question.original_question,
            valid=enh_question.valid,
            question=enh_question.question,
            answer=None,
            explanation=enh_question.explanation,
            context=None,
        )
        new_quest = await QuestionsRepository(session).create_question(question_create)

        state.remaining_questions -= 1
        state.questions_asked += 1
        state = await CountrydleStateRepository(session).update_countrydle_state(state)

        return InvalidQuestionDisplay.model_validate(new_quest)

    question_create, question_vector = await gutils.ask_question(
        question=enh_question,
        day_country=day_country,
        user=user,
        session=session,
    )

    new_quest = await QuestionsRepository(session).create_question(question_create)

    await add_question_to_qdrant(new_quest, question_vector, day_country.country_id)

    state.remaining_questions -= 1
    state.questions_asked += 1
    state = await CountrydleStateRepository(session).update_countrydle_state(state)

    return QuestionDisplay.model_validate(new_quest)
