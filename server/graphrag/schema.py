from .kuzu_client import get_connection

def init_schema():
    conn = get_connection()
    
    # Drop existing tables if they exist (for development/reset)
    tables = [
        "HAS_CONCEPT", "BORDERS", "Country", "Concept"
    ]
    
    for table in tables:
        try:
            conn.execute(f"DROP TABLE {table}")
        except Exception:
            pass

    print("Creating KuzuDB Schema for Countrydle...")

    # Node Tables
    # Country: The main subject of the game
    conn.execute("CREATE NODE TABLE Country(name STRING, capital STRING, population INT64, area DOUBLE, PRIMARY KEY (name))")
    
    # Concept: Any related entity (Continent, Organization, Currency, Language, Religion, Climate, etc.)
    conn.execute("CREATE NODE TABLE Concept(name STRING, category STRING, PRIMARY KEY (name))")

    # Relationship Tables
    # Borders: Physical adjacency between countries
    conn.execute("CREATE REL TABLE BORDERS(FROM Country TO Country)")
    
    # HasConcept: A generic relationship to capture various facts
    # e.g., (Poland)-[:HAS_CONCEPT {relationship: 'Member Of'}]->(EU)
    # e.g., (Poland)-[:HAS_CONCEPT {relationship: 'Located In'}]->(Europe)
    # e.g., (Poland)-[:HAS_CONCEPT {relationship: 'Uses Currency'}]->(Zloty)
    conn.execute("CREATE REL TABLE HAS_CONCEPT(FROM Country TO Concept, relationship STRING)")

    print("Schema initialized successfully.")

if __name__ == "__main__":
    init_schema()

if __name__ == "__main__":
    init_schema()
