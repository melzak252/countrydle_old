import asyncio
import logging
import os
from pathlib import Path
from typing import List

from db.models import Country, Document, Fragment
from db.repositories.country import CountryRepository
from db.repositories.document import DocumentRepository, FragmentRepository
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
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client: QdrantClient = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


async def init_qdrant(session: AsyncSession):
    if not client.collection_exists("questions"):
        client.create_collection(
            collection_name="questions",
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )
        client.create_payload_index(
            collection_name="questions", field_name="country_id", field_schema="integer"
        )

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
        )

    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="country_id",
        field_schema=IntegerIndexParams(
            type="integer", is_principal=True, lookup=True, range=False
        ),
    )


async def populate_qdrant(session: AsyncSession):

    d_repo = DocumentRepository(session)
    c_repo = CountryRepository(session)
    f_repo = FragmentRepository(session)
    countries: List[Country] = await c_repo.get_all_countries()
    num_c = len(countries)
    for i, country in enumerate(countries):
        logging.info(f"Country {i+1}/{num_c}: {country.name}")
        doc: Document = await d_repo.get_doc_for_country(country.id)
        fragments: List[Fragment] = await f_repo.get_fragments_for_doc(doc.id)
        ids = [fragment.id for fragment in fragments]
        points = []

        if len(get_points(client, COLLECTION_NAME, ids)) == len(ids):
            continue

        for fragment in fragments:

            embedding = fragment.embedding

            point = PointStruct(
                id=fragment.id,
                vector=embedding,
                payload={
                    "country_id": country.id,
                    "country_name": country.name,
                    "fragment_text": fragment.text,
                },
            )
            points.append(point)

        if points:
            client.upsert(collection_name=COLLECTION_NAME, points=points)


def get_qdrant_client():
    """Returns the initialized Qdrant client."""
    return client


def close_qdrant_client():
    """Closes the Qdrant client if it's open."""
    global client
    if client:
        client.close()
