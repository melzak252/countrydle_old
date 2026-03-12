import logging
from db import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.countrydle import CountrydleHistory, LeaderboardEntry, UserStatistics
from db.repositories.countrydle import CountrydleRepository, CountrydleStateRepository
from db.models.user import User
from db.repositories.user import UserRepository
from users.utils import get_current_user


load_dotenv()

router = APIRouter(prefix="/statistics")


@router.get("/history", response_model=CountrydleHistory)
async def gey_history(session: AsyncSession = Depends(get_db)):
    daily_countries = await CountrydleRepository(session).get_countrydle_history()
    countries_count = await CountrydleRepository(session).get_countries_count()
    return CountrydleHistory(
        daily_countries=daily_countries,
        countries_count=countries_count,
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(type: str = "monthly", session: AsyncSession = Depends(get_db)):
    leaderboard = await CountrydleRepository(session).get_leaderboard(type)
    return leaderboard


@router.get("/history/me")
async def gey_history(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
):
    data = await CountrydleStateRepository(session).get_player_countrydle_states(user)
    return data


@router.get("/users/{username}", response_model=UserStatistics)
async def get_user_statistics(username: str, session: AsyncSession = Depends(get_db)):
    user = await UserRepository(session).get_user(username)
    profile = await CountrydleRepository(session).get_user_statistics(user)
    return profile
