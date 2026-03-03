import asyncio
import logging
from contextlib import asynccontextmanager

import users.crud as ucrud
from db import AsyncSessionLocal, get_engine

from db.models import *  # noqa: F403
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
import utils
from utils.graph import graph_manager


async def init_models(engine: AsyncEngine):
    import os
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        db_url = db_url.replace("+asyncpg", "")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    
    try:
        print("Starting database migrations...", flush=True)
        # Run in a thread to avoid blocking the event loop
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
        print("Database migrations applied successfully.", flush=True)
    except Exception as e:
        print(f"Error applying migrations: {e}", flush=True)
        raise e


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    try:
        await init_models(engine)

        async with AsyncSessionLocal() as session:
            await ucrud.add_base_permissions(session)
            # Verify Neo4j connection
            try:
                graph_manager.graph.query("RETURN 1")
                print("Neo4j connection verified.", flush=True)
            except Exception as e:
                print(f"Warning: Could not connect to Neo4j: {e}", flush=True)

        utils.scheduler.start()

        yield
    except ConnectionRefusedError:
        logging.error("Exiting application due to database connection failure.")
        await asyncio.sleep(10)
        raise
    except Exception as e:
        logging.error(f"Exiting application due to error: {e}", exc_info=True)
        raise e
    finally:
        try:
            logging.info("Shutting down application...")
            utils.scheduler.shutdown(wait=True)
            await engine.dispose()
            logging.info("Application shutdown complete.")
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")

