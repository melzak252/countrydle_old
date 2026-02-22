import asyncio
import os
from pathlib import Path
from typing import List

from db.models import Country
from db.models.fragment import CountryFragment, PowiatFragment, WojewodztwoFragment, USStateFragment
from db.repositories.country import CountryRepository
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import Distance, PointStruct, VectorParams, IntegerIndexParams
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .utils import get_points, upsert_in_batches

load_dotenv()

EMBEDDING_SIZE = int(os.getenv("EMBEDDING_SIZE", "1536"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Collection names
COLLECTIONS = {
    "countries": "countries",
    "powiaty": "powiaty",
    "wojewodztwa": "wojewodztwa",
    "us_states": "us_states",
    "countries_questions": "countries_questions",
    "powiaty_questions": "powiaty_questions",
    "wojewodztwa_questions": "wojewodztwa_questions",
    "us_states_questions": "us_states_questions",
}

client: QdrantClient = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


async def sync_from_postgres(session: AsyncSession, collection_name: str):
    """Syncs data from Postgres to Qdrant if counts differ."""
    model = None
    if collection_name == "countries": model = CountryFragment
    elif collection_name == "powiaty": model = PowiatFragment
    elif collection_name == "wojewodztwa": model = WojewodztwoFragment
    elif collection_name == "us_states": model = USStateFragment
    
    if not model:
        return

    try:
        # Get Postgres count
        res = await session.execute(select(func.count(model.id)))
        pg_count = res.scalar() or 0

        # Get Qdrant count
        info = client.get_collection(collection_name)
        qdrant_count = info.points_count or 0

        if pg_count == qdrant_count:
            print(f"Collection {collection_name} is up to date ({pg_count} points).")
            return
            
        print(f"Collection {collection_name} count mismatch (PG: {pg_count}, Qdrant: {qdrant_count}). Syncing...")
    except Exception as e:
        print(f"Error checking counts for {collection_name}: {e}")
        return
    
    print(f"Fetching {pg_count} fragments from Postgres for collection '{collection_name}'...")
    points = []
    if collection_name == "countries":
        res = await session.execute(select(CountryFragment))
        fragments = res.scalars().all()
        for f in fragments:
            points.append(PointStruct(id=int(f.id), vector=list(f.embedding), payload={"country_id": f.country_id, "fragment_text": f.text}))
    elif collection_name == "powiaty":
        res = await session.execute(select(PowiatFragment))
        fragments = res.scalars().all()
        for f in fragments:
            points.append(PointStruct(id=int(f.id), vector=list(f.embedding), payload={"powiat_id": f.powiat_id, "fragment_text": f.text}))
    elif collection_name == "wojewodztwa":
        res = await session.execute(select(WojewodztwoFragment))
        fragments = res.scalars().all()
        for f in fragments:
            points.append(PointStruct(id=int(f.id), vector=list(f.embedding), payload={"wojewodztwo_id": f.wojewodztwo_id, "fragment_text": f.text}))
    elif collection_name == "us_states":
        res = await session.execute(select(USStateFragment))
        fragments = res.scalars().all()
        for f in fragments:
            points.append(PointStruct(id=int(f.id), vector=list(f.embedding), payload={"us_state_id": f.us_state_id, "fragment_text": f.text}))

    if points:
        print(f"Starting upsert of {len(points)} points to collection '{collection_name}'...")
        upsert_in_batches(client, collection_name, points, batch_size=200)
        print(f"Successfully synced {len(points)} points to {collection_name}")
    else:
        print(f"No points to sync for collection '{collection_name}'.")


async def init_qdrant(session: AsyncSession):
    print("Initializing Qdrant collections...")
    for name in COLLECTIONS.values():
        if not client.collection_exists(name):
            print(f"Creating collection '{name}'...")
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
            )
            
            # Add payload indexes
            field_name = ""
            if name.endswith("_questions"):
                if name.startswith("countries"): field_name = "country_id"
                elif name.startswith("powiaty"): field_name = "powiat_id"
                elif name.startswith("wojewodztwa"): field_name = "wojewodztwo_id"
                elif name.startswith("us_states"): field_name = "us_state_id"
                
                if field_name:
                    print(f"Creating payload index for '{field_name}' in collection '{name}'...")
                    client.create_payload_index(collection_name=name, field_name=field_name, field_schema="integer")
            else:
                if name == "countries": field_name = "country_id"
                elif name == "powiaty": field_name = "powiat_id"
                elif name == "wojewodztwa": field_name = "wojewodztwo_id"
                elif name == "us_states": field_name = "us_state_id"

                if field_name:
                    print(f"Creating payload index for '{field_name}' in collection '{name}'...")
                    client.create_payload_index(
                        collection_name=name,
                        field_name=field_name,
                        field_schema=IntegerIndexParams(type="integer", is_principal=True, lookup=True, range=False),
                    )
        
        # Sync data if needed (only for main fragment collections)
        if name in ["countries", "powiaty", "wojewodztwa", "us_states"]:
            await sync_from_postgres(session, name)

    if not client.collection_exists("questions"):
        print("Creating collection 'questions'...")
        client.create_collection(
            collection_name="questions",
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )


def get_qdrant_client():
    return client


def close_qdrant_client():
    global client
    if client:
        client.close()
