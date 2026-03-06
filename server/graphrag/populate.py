import os
import json
import glob
import argparse
import time
from openai import OpenAI
from .kuzu_client import get_connection
from .schema import init_schema

client = OpenAI()


def extract_data_from_chunk(content, entity_type, chunk_index, total_chunks):
    """
    Uses LLM to extract structured data from a chunk of markdown content.
    """
    system_prompt = f"""
    You are a data extractor for a geography graph database.
    Extract structured information from the following chunk ({chunk_index+1}/{total_chunks}) of markdown content about a {entity_type}.
    
    Extract:
    1. Basic properties (only if found): capital, population (INT64), area (DOUBLE).
    2. Neighbors: A list of names of other {entity_type}s that border this one.
    3. Concepts: A comprehensive list of identifying features and relationships. 
       Look for EVERYTHING that could be used to distinguish or group this {entity_type} with others:
       - Geographic: Continents, Regions, Sub-regions, Time Zones, Climate Zones.
       - Physical: Shared Rivers, Lakes, Seas, Oceans, Mountain Ranges, Deserts.
       - Political: Organizations (UN, EU, NATO, G7, ASEAN, AU, etc.), Trading Blocs, Government Type.
       - Cultural: Official Languages, Common Languages, Major Religions, Ethnic Groups.
       - Economic: Currencies, Major Exports, Income Level (World Bank).
       - Infrastructure: Driving Side (Left/Right), Calling Code, Internet TLD.
       - Historical: Former Empires, Colonial History, Independence Year.
       - Landmarks: World Heritage Sites, Famous Natural or Man-made Landmarks.
       
       For each concept, provide:
       - name: The specific name (e.g., "UTC+1", "Atlantic Ocean", "Roman Catholicism", "Right-hand traffic").
       - category: The broad category (e.g., "Time Zone", "Ocean", "Religion", "Driving Side").
       - relationship: A descriptive verb phrase (e.g., "Located In", "Borders", "Practices", "Drives On", "Member Of").

    Output format: JSON
    {{
        "name": "Name of the {entity_type} (if known, otherwise null)",
        "properties": {{
            "capital": "...",
            "population": 123456,
            "area": 123.45
        }},
        "neighbors": ["Neighbor 1", "Neighbor 2"],
        "concepts": [
            {{"name": "...", "category": "...", "relationship": "..."}}
        ]
    }}
    """

    model = os.getenv("QUIZ_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": content,
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def extract_data_from_md(content, entity_type):
    """
    Splits content into chunks and aggregates extracted data.
    """
    chunk_size = 12000
    overlap = 1000
    chunks = []
    
    start = 0
    while start < len(content):
        end = start + chunk_size
        chunks.append(content[start:end])
        if end >= len(content):
            break
        start = end - overlap

    aggregated_data = {
        "name": None,
        "properties": {},
        "neighbors": set(),
        "concepts": {} # Use dict to deduplicate by name
    }

    print(f"  Splitting into {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        print(f"    Processing chunk {i+1}/{len(chunks)}...")
        data = extract_data_from_chunk(chunk, entity_type, i, len(chunks))
        
        if data.get("name") and not aggregated_data["name"]:
            aggregated_data["name"] = data["name"]
            
        # Merge properties (prefer non-null/non-zero)
        props = data.get("properties", {})
        for k, v in props.items():
            if v and v != "..." and v != 0:
                aggregated_data["properties"][k] = v
        
        # Merge neighbors
        for n in data.get("neighbors", []):
            if n and n != "...":
                aggregated_data["neighbors"].add(n)
                
        # Merge concepts
        for c in data.get("concepts", []):
            c_name = c.get("name")
            if c_name and c_name != "...":
                # Store by name to deduplicate, but keep the most complete info
                aggregated_data["concepts"][c_name] = c

    # Convert back to list format for populate_data
    return {
        "name": aggregated_data["name"],
        "properties": aggregated_data["properties"],
        "neighbors": list(aggregated_data["neighbors"]),
        "concepts": list(aggregated_data["concepts"].values())
    }


def populate_data(all_data, entity_type):
    """
    Populates KuzuDB with extracted data.
    """
    conn = get_connection()
    
    # Pass 1: Create Nodes
    print("Creating nodes...")
    for data in all_data:
        name = data.get("name", "").replace("'", "''")
        if not name:
            continue

        props = data.get("properties", {})
        capital = props.get("capital", "").replace("'", "''")
        pop = props.get("population", 0)
        # Ensure pop is int
        try:
            pop = int(pop)
        except:
            pop = 0

        area = props.get("area", 0.0)
        # Ensure area is float
        try:
            area = float(area)
        except:
            area = 0.0

        # Create Country/Entity node
        try:
            conn.execute(
                f"MERGE (n:{entity_type} {{name: '{name}'}}) ON CREATE SET n.capital = '{capital}', n.population = {pop}, n.area = {area}"
            )
        except Exception as e:
            print(f"Error creating node {name}: {e}")

        # Create Concept nodes
        for concept in data.get("concepts", []):
            c_name = concept.get("name", "").replace("'", "''")
            c_cat = concept.get("category", "").replace("'", "''")
            if not c_name:
                continue
            try:
                conn.execute(
                    f"MERGE (c:Concept {{name: '{c_name}'}}) ON CREATE SET c.category = '{c_cat}'"
                )
            except Exception as e:
                print(f"Error creating concept {c_name}: {e}")

    # Pass 2: Create Relationships
    print("Creating relationships...")
    for data in all_data:
        name = data.get("name", "").replace("'", "''")
        if not name:
            continue

        # Borders
        for neighbor in data.get("neighbors", []):
            n_name = neighbor.replace("'", "''")
            try:
                # Note: BORDERS is the table name in our schema
                conn.execute(
                    f"MATCH (a:{entity_type} {{name: '{name}'}}), (b:{entity_type} {{name: '{n_name}'}}) MERGE (a)-[:BORDERS]->(b)"
                )
            except Exception as e:
                # Neighbor might not exist yet or other error
                pass

        # Concepts
        for concept in data.get("concepts", []):
            c_name = concept.get("name", "").replace("'", "''")
            rel_desc = concept.get("relationship", "").replace("'", "''")
            if not c_name:
                continue
            try:
                conn.execute(
                    f"MATCH (a:{entity_type} {{name: '{name}'}}), (c:Concept {{name: '{c_name}'}}) MERGE (a)-[:HAS_CONCEPT {{relationship: '{rel_desc}'}}]->(c)"
                )
            except Exception as e:
                print(f"Error creating rel between {name} and {c_name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Populate KuzuDB from markdown files.")
    parser.add_argument("--folder", help="Path to the folder containing .md files")
    parser.add_argument("--file", help="Path to a single .md file")
    parser.add_argument(
        "--type", default="Country", help="Entity type (Country, USState, etc.)"
    )
    parser.add_argument(
        "--init", action="store_true", help="Initialize schema before population"
    )
    parser.add_argument(
        "--limit", type=int, help="Limit the number of files to process"
    )
    parser.add_argument(
        "--save-json", help="Path to save the extracted data as JSON"
    )
    parser.add_argument(
        "--delay", type=float, default=1.0, help="Delay in seconds between LLM calls"
    )

    args = parser.parse_args()

    if args.init:
        init_schema()

    files = []
    if args.file:
        files = [args.file]
    elif args.folder:
        files = glob.glob(os.path.join(args.folder, "*.md"))
    else:
        print("Error: Either --folder or --file must be provided.")
        return

    if not files:
        print("No files found.")
        return

    if args.limit:
        files = files[:args.limit]

    all_data = []
    print(f"Processing {len(files)} files...")
    for i, file_path in enumerate(files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                data = extract_data_from_md(content, args.type)
                all_data.append(data)
                print(f"[{i+1}/{len(files)}] Extracted data for {data.get('name', 'Unknown')}")
                
                if i < len(files) - 1:
                    time.sleep(args.delay)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if args.save_json:
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        print(f"Saved extracted data to {args.save_json}")

    populate_data(all_data, args.type)
    print("Population complete.")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
