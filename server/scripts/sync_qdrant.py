import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the server directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env from server directory
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
)

from db import AsyncSessionLocal
from qdrant import sync_from_postgres, init_qdrant

async def main():
    print("Starting Qdrant synchronization from Postgres...")
    async with AsyncSessionLocal() as session:
        try:
            # Ensure collections exist first
            await init_qdrant(session)
            
            collections = ["countries", "powiaty", "wojewodztwa", "us_states"]
            for collection in collections:
                print(f"Syncing collection: {collection}...")
                await sync_from_postgres(session, collection)
                
            print("Qdrant synchronization completed successfully.")
        except Exception as e:
            print(f"An error occurred during Qdrant synchronization: {e}")

if __name__ == "__main__":
    asyncio.run(main())
