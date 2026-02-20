import asyncio
import sys
import os
import json
import csv
import logging
import uuid
from dotenv import load_dotenv
from tqdm import tqdm

# Add the server directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env from server directory
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
)

from db import AsyncSessionLocal
import qdrant
import qdrant.utils as qutils
from db.models.wojewodztwo import Wojewodztwo
from db.repositories.wojewodztwo import WojewodztwoRepository
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client.models import PointStruct


async def populate_wojewodztwa(session: AsyncSession):
    w_rep = WojewodztwoRepository(session)
    wojewodztwa = await w_rep.get_all()

    if wojewodztwa:
        print("Wojewodztwa already populated in DB.")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(base_dir)
    data_dir = os.path.join(base_dir, "data")
    csv_file = os.path.join(data_dir, "wojewodztwa.csv")

    if not os.path.exists(csv_file):
        logging.error(f"{csv_file} not found!")
        return

    logging.info("Populating wojewodztwa from CSV...")
    
    # Read all rows first to use tqdm
    rows = []
    with open(csv_file, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} wojewodztwa to process.")

    for row in tqdm(rows, desc="Populating Wojewodztwa"):
        # Map 'name' from CSV to 'nazwa' in model
        nazwa = row.get("name")
        md_filename = row.get("md_file")

        if not nazwa or not md_filename:
            logging.warning(f"Skipping row: missing name or md_file")
            continue

        wojewodztwo = Wojewodztwo(nazwa=nazwa)
        session.add(wojewodztwo)

        try:
            await session.commit()
            await session.refresh(wojewodztwo)
        except Exception as ex:
            await session.rollback()
            raise ex

        # Normalize path separators and construct full path
        md_rel_path = md_filename.replace("\\", "/")
        md_path = md_rel_path

        try:
            with open(md_path, encoding="utf8") as md_file:
                md_content = md_file.read()

            doc_fragments = qutils.split_document(md_content)
            points = []

            embedding_model = qdrant.EMBEDDING_MODEL
            if not embedding_model:
                raise ValueError("EMBEDDING_MODEL environment variable is not set")

            fragment_texts = [fragment.page_content for fragment in doc_fragments]
            embeddings = qutils.get_bulk_embedding(fragment_texts, embedding_model)

            for i, fragment in enumerate(doc_fragments):
                point_id = str(uuid.uuid4())

                point = PointStruct(
                    id=point_id,
                    vector=embeddings[i],
                    payload={
                        "wojewodztwo_id": wojewodztwo.id,
                        "wojewodztwo_nazwa": wojewodztwo.nazwa,
                        "fragment_text": fragment.page_content,
                    },
                )
                points.append(point)

            if points:
                qutils.upsert_in_batches(
                    client=qdrant.client,
                    collection_name="wojewodztwa",
                    points=points,
                    batch_size=50,
                    max_retries=3
                )

        except FileNotFoundError:
            logging.warning(
                f"Markdown file not found for {wojewodztwo.nazwa}: {md_path}"
            )


async def main():
    print("Starting wojewodztwa population...")
    async with AsyncSessionLocal() as session:
        await qdrant.init_qdrant(session)
        try:
            await populate_wojewodztwa(session)
            print("Wojewodztwa population completed successfully.")
        except Exception as e:
            print(f"An error occurred during wojewodztwa population: {e}")


if __name__ == "__main__":
    asyncio.run(main())
