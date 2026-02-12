from typing import List, Tuple

from db.models import DayCountry, Fragment, Question
from db.repositories.document import FragmentRepository
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import (
    FieldCondition,
    Filter,
    MatchValue,
    GroupsResult,
    PointGroup,
    ScoredPoint,
)
from sqlalchemy.ext.asyncio import AsyncSession
import qdrant

from qdrant_client.models import PointStruct

from .vectorize import get_embedding


def split_document(content: str) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, length_function=len
    )

    fragments = text_splitter.create_documents([content])
    return fragments


def get_points(client: QdrantClient, collection_name: str, ids: list[int]):
    try:
        # Try to get the point by its ID
        points = client.retrieve(collection_name=collection_name, ids=ids)
        return points
    except UnexpectedResponse:
        return []


def search_matches(
    collection_name: str,
    query_vector: list,
    country_id: int = None,
    limit: int = 5,
) -> List[ScoredPoint]:
    search_result: GroupsResult = qdrant.client.query_points_groups(
        collection_name=collection_name,
        query=query_vector,  # Use the query vector to search for similar vectors
        group_by="country_id",  # Group results by country_id
        group_size=limit,  # Return up to 5 points per group
        limit=1,  # Limit to 3 groups (you can adjust as needed)
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="country_id",
                    match=MatchValue(value=country_id),  # Strict match for country_id
                )
            ]
        ),
        with_payload=True,
    )
    if not search_result.groups:
        return []
    group, *_ = search_result.groups
    return group.hits


async def get_fragments_matching_question(
    question: str, day: DayCountry, collection_name: str, session: AsyncSession
) -> Tuple[list[Fragment], List[float]]:
    query = question
    query_vector = get_embedding(query, qdrant.EMBEDDING_MODEL)

    points: List[ScoredPoint] = search_matches(
        collection_name=collection_name,
        query_vector=query_vector,
        country_id=day.country_id,
    )
    points.sort(key=lambda x: int(x.id))
    f_repo = FragmentRepository(session)
    fragments = []
    for point in points:
        fragment = await f_repo.get(int(point.id))
        fragments.append(fragment)

    return fragments, query_vector


async def add_question_to_qdrant(
    question: Question, vector: List[float], country_id: int
):
    point = PointStruct(
        id=question.id,
        vector=vector,
        payload={
            "country_id": country_id,
            "question_text": question.question,
            "answer": question.answer,
            "explonation": question.explanation,
        },
    )
    qdrant.client.upsert(collection_name="questions", points=[point])
