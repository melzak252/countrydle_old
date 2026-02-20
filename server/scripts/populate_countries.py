import asyncio
import sys
import os
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
from db.models import Country
from db.repositories.country import CountryRepository
from sqlalchemy.ext.asyncio import AsyncSession
from qdrant_client.models import PointStruct


async def populate_countries(session: AsyncSession):
    c_rep = CountryRepository(session)
    countries = await c_rep.get_all_countries()

    if countries:
        print("Countries already populated in DB.")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(base_dir)
    data_dir = os.path.join(base_dir, "data")
    csv_file = os.path.join(data_dir, "countries.csv")

    if not os.path.exists(csv_file):
        logging.error(f"{csv_file} not found!")
        return

    # Read all rows first to use tqdm
    rows = []
    with open(csv_file, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} countries to process.")

    for row in tqdm(rows, desc="Populating Countries"):
        name = row.get("name")
        md_filename = row.get("md_file")

        if not name or not md_filename:
            logging.warning(f"Skipping row: missing name or md_file")
            continue

        # Normalize path separators and construct full path
        md_rel_path = md_filename.replace("\\", "/")
        md_path = md_rel_path

        country = Country(
            name=name,
            official_name=name,  # Defaulting to name as it's not in CSV
            wiki="",  # Defaulting to empty as it's not in CSV
            md_file=md_path,
        )

        # Read the markdown content for the country
        try:
            with open(md_path, encoding="utf8") as md_file:
                md_content = md_file.read()
        except FileNotFoundError:
            logging.warning(
                f"Markdown file not found for {country.name}: {md_path}"
            )
            continue

        session.add(country)
        try:
            await session.commit()  # Commit to get the ID
            await session.refresh(country)
        except Exception as ex:
            await session.rollback()
            raise ex

        doc_fragments = qutils.split_document(md_content)
        
        embedding_model = qdrant.EMBEDDING_MODEL
        if not embedding_model:
            raise ValueError("EMBEDDING_MODEL environment variable is not set")

        fragment_texts = [fragment.page_content for fragment in doc_fragments]
        embeddings = qutils.get_bulk_embedding(fragment_texts, embedding_model)

        points = []
        for i, fragment in enumerate(doc_fragments):
            point_id = str(uuid.uuid4())

            point = PointStruct(
                id=point_id,
                vector=embeddings[i],
                payload={
                    "country_id": country.id,
                    "country_name": country.name,
                    "fragment_text": fragment.page_content,
                },
            )
            points.append(point)

        if points:
            qutils.upsert_in_batches(
                client=qdrant.client,
                collection_name="countries",
                points=points,
                batch_size=50,
                max_retries=3
            )

    print("Countries population finished.")


async def main():
    print("Starting database population...")
    async with AsyncSessionLocal() as session:
        await qdrant.init_qdrant(session)
        try:
            await populate_countries(session)
            print("Database population completed successfully.")
        except Exception as e:
            print(f"An error occurred during database population: {e}")


if __name__ == "__main__":
    asyncio.run(main())
