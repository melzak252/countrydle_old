import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Add the server directory to sys.path to allow imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

async def drop_all_tables():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        print("Dropping all tables...")
        # Reflect tables is hard with async, so we just use CASCADE on public schema or drop tables if we know them.
        # But dropping schema public cascade is drastic.
        # Better to drop specific tables if we know them, or use a query to find all tables.
        
        # This query finds all tables in public schema
        result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = result.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"Dropping table {table_name}...")
            await conn.execute(text(f"DROP TABLE IF EXISTS \"{table_name}\" CASCADE"))
            
        print("All tables dropped.")

if __name__ == "__main__":
    asyncio.run(drop_all_tables())
