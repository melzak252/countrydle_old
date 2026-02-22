import asyncio
import sys
import os
import logging
import uuid
from dotenv import load_dotenv
from tqdm import tqdm
from sqlalchemy import select

# Add the server directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env from server directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from db import AsyncSessionLocal
import qdrant
import qdrant.utils as qutils
from db.models.fragment import CountryFragment, PowiatFragment, WojewodztwoFragment, USStateFragment
from qdrant_client.models import PointStruct

async def sync_countries(session):
    print("Syncing countries from Postgres to Qdrant...")
    res = await session.execute(select(CountryFragment).order_by(CountryFragment.id))
    fragments = res.scalars().all()
    
    points = []
    for f in fragments:
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=f.embedding,
            payload={
                "country_id": f.country_id,
                "fragment_text": f.text,
            }
        ))
    
    if points:
        qutils.upsert_in_batches(qdrant.client, "countries", points, batch_size=100)
    print(f"Synced {len(points)} country fragments.")

async def sync_powiaty(session):
    print("Syncing powiaty from Postgres to Qdrant...")
    res = await session.execute(select(PowiatFragment).order_by(PowiatFragment.id))
    fragments = res.scalars().all()
    
    points = []
    for f in fragments:
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=f.embedding,
            payload={
                "powiat_id": f.powiat_id,
                "fragment_text": f.text,
            }
        ))
    
    if points:
        qutils.upsert_in_batches(qdrant.client, "powiaty", points, batch_size=100)
    print(f"Synced {len(points)} powiat fragments.")

async def sync_wojewodztwa(session):
    print("Syncing wojewodztwa from Postgres to Qdrant...")
    res = await session.execute(select(WojewodztwoFragment).order_by(WojewodztwoFragment.id))
    fragments = res.scalars().all()
    
    points = []
    for f in fragments:
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=f.embedding,
            payload={
                "wojewodztwo_id": f.wojewodztwo_id,
                "fragment_text": f.text,
            }
        ))
    
    if points:
        qutils.upsert_in_batches(qdrant.client, "wojewodztwa", points, batch_size=100)
    print(f"Synced {len(points)} wojewodztwo fragments.")

async def sync_us_states(session):
    print("Syncing US states from Postgres to Qdrant...")
    res = await session.execute(select(USStateFragment).order_by(USStateFragment.id))
    fragments = res.scalars().all()
    
    points = []
    for f in fragments:
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=f.embedding,
            payload={
                "us_state_id": f.us_state_id,
                "fragment_text": f.text,
            }
        ))
    
    if points:
        qutils.upsert_in_batches(qdrant.client, "us_states", points, batch_size=100)
    print(f"Synced {len(points)} US state fragments.")

async def main():
    async with AsyncSessionLocal() as session:
        await qdrant.init_qdrant(session)
        try:
            await sync_countries(session)
            await sync_powiaty(session)
            await sync_wojewodztwa(session)
            await sync_us_states(session)
            print("\nAll data successfully synced from Postgres to Qdrant!")
        except Exception as e:
            print(f"Error during sync: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
