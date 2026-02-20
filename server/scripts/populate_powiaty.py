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
from db.models.powiat import Powiat
from db.repositories.powiatdle import PowiatRepository
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client.models import PointStruct


async def populate_powiaty(session: AsyncSession):
    p_rep = PowiatRepository(session)
    powiaty = await p_rep.get_all()

    if powiaty:
        print("Powiaty already populated in DB.")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(base_dir)
    data_dir = os.path.join(base_dir, "data")
    csv_file = os.path.join(data_dir, "powiaty.csv")

    if not os.path.exists(csv_file):
        logging.error(f"{csv_file} not found!")
        return

    logging.info("Populating powiaty from CSV...")
    
    # Read all rows first to use tqdm
    rows = []
    with open(csv_file, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} powiaty to process.")

    for row in tqdm(rows, desc="Populating Powiaty"):
        # Map 'name' from CSV to 'nazwa' in model
        nazwa = row.get("name")
        md_filename = row.get("md_file")

        if not nazwa or not md_filename:
            logging.warning(f"Skipping row: missing name or md_file")
            continue

        powiat = Powiat(nazwa=nazwa)
        session.add(powiat)

        try:
            await session.commit()
            await session.refresh(powiat)
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
                        "powiat_id": powiat.id,
                        "powiat_nazwa": powiat.nazwa,
                        "fragment_text": fragment.page_content,
                    },
                )
                points.append(point)

            if points:
                qutils.upsert_in_batches(
                    client=qdrant.client,
                    collection_name="powiaty",
                    points=points,
                    batch_size=50,
                    max_retries=3
                )

        except FileNotFoundError:
            logging.warning(
                f"Markdown file not found for {powiat.nazwa}: {md_path}"
            )


async def main():
    print("Starting powiaty population...")
    async with AsyncSessionLocal() as session:
        await qdrant.init_qdrant(session)
        try:
            await populate_powiaty(session)
            print("Powiaty population completed successfully.")
        except Exception as e:
            print(f"An error occurred during powiaty population: {e}")


if __name__ == "__main__":
    asyncio.run(main())
