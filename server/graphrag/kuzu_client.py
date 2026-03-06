import kuzu
import os

# Path to the Kuzu database directory
KUZU_DB_PATH = os.getenv("KUZU_DB_PATH", "databases/kuzu_db")

# Ensure the directory exists
os.makedirs(os.path.dirname(KUZU_DB_PATH), exist_ok=True)

# Initialize the database and connection
db = kuzu.Database(KUZU_DB_PATH)
conn = kuzu.Connection(db)

def get_connection():
    return conn

def get_db():
    return db
