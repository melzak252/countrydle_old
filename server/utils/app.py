import asyncio
import logging
from contextlib import asynccontextmanager

import users.crud as ucrud
from db import AsyncSessionLocal, get_engine

from db.models import *  # noqa: F403
from db.base import Base
from fastapi import FastAPI
from qdrant import close_qdrant_client, init_qdrant
from sqlalchemy.ext.asyncio import AsyncEngine
import utils


async def init_models(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Database connection established and models created.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    try:
        await init_models(engine)
        utils.scheduler.start()

        async with AsyncSessionLocal() as session:
            await ucrud.add_base_permissions(session)
            await init_qdrant(session)


        await utils.generate_day_countries()
        await utils.check_streaks()

        yield
    except ConnectionRefusedError:
        logging.error("Exiting application due to database connection failure.")
        await asyncio.sleep(10)
        raise
    except Exception as e:
        logging.error("Exiting application due to error.")
        raise e
    finally:
        try:
            logging.info("Shutting down application...")
            utils.scheduler.shutdown(wait=True)
            close_qdrant_client()
            await engine.dispose()
            logging.info("Application shutdown complete.")
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")
