import asyncio
import logging
import os
from pathlib import Path
from typing import List

from db.models import Country
from db.repositories.country import CountryRepository
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import Distance, PointStruct, VectorParams, IntegerIndexParams
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import get_points

load_dotenv()

EMBEDDING_SIZE = int(os.getenv("EMBEDDING_SIZE"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = int(os.getenv("QDRANT_PORT"))

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

# For backward compatibility if needed, but we should prefer the dict
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client: QdrantClient = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


async def init_qdrant(session: AsyncSession):
    for name in COLLECTIONS.values():
        if not client.collection_exists(name):
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
            )
            
            # Add payload indexes based on collection type
            if name.endswith("_questions"):
                # Questions collections
                field_name = ""
                if name.startswith("countries"):
                    field_name = "country_id"
                elif name.startswith("powiaty"):
                    field_name = "powiat_id"
                elif name.startswith("wojewodztwa"):
                    field_name = "wojewodztwo_id"
                elif name.startswith("us_states"):
                    field_name = "us_state_id"
                
                if field_name:
                    client.create_payload_index(
                        collection_name=name, field_name=field_name, field_schema="integer"
                    )
            else:
                # Fragments collections
                field_name = ""
                if name == "countries":
                    field_name = "country_id"
                elif name == "powiaty":
                    field_name = "powiat_id"
                elif name == "wojewodztwa":
                    field_name = "wojewodztwo_id"
                elif name == "us_states":
                    field_name = "us_state_id"

                if field_name:
                    client.create_payload_index(
                        collection_name=name,
                        field_name=field_name,
                        field_schema=IntegerIndexParams(
                            type="integer", is_principal=True, lookup=True, range=False
                        ),
                    )

    # Legacy "questions" collection if still used anywhere
    if not client.collection_exists("questions"):
        client.create_collection(
            collection_name="questions",
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )


def get_qdrant_client():
    """Returns the initialized Qdrant client."""
    return client


def close_qdrant_client():
    """Closes the Qdrant client if it's open."""
    global client
    if client:
        client.close()
