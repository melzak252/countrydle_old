import os
import json
import asyncio
import argparse
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini" 

# Initialize Neo4j
print(f"Connecting to Neo4j at {NEO4J_URI}...")
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
)
try:
    test_res = graph.query("RETURN 1 as val")
    print(f"Neo4j connection test successful: {test_res}")
except Exception as e:
    print(f"Neo4j connection test failed: {e}")
    exit(1)

# Initialize LLM
llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
transformer = LLMGraphTransformer(llm=llm)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

GAME_CONFIG = {
    "countries": {"dir": "data/countries", "label": "Country", "node_label": "CountryNode"},
    "powiaty": {"dir": "data/counties", "label": "Powiat", "node_label": "PowiatNode"},
    "us_states": {"dir": "data/us_states", "label": "USState", "node_label": "USStateNode"},
    "wojewodztwa": {"dir": "data/voivodeships", "label": "Wojewodztwo", "node_label": "WojewodztwoNode"}
}

async def process_game(game_key: str):
    config = GAME_CONFIG[game_key]
    directory_path = config["dir"]
    game_label = config["label"]
    node_label = config["node_label"]

    print(f"\n--- Populating GraphRAG for: {game_label} ---")
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist. Skipping.")
        return

    for filename in os.listdir(directory_path):
        if filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)
            entity_name = filename.replace(".md", "").replace("_", " ")
            
            print(f"  Extracting graph for: {entity_name}")
            
            try:
                loader = UnstructuredMarkdownLoader(file_path)
                raw_docs = loader.load()
                docs = text_splitter.split_documents(raw_docs)
                print(f"    Split into {len(docs)} chunks.")
                
                for doc in docs:
                    doc.metadata["entity"] = entity_name
                    doc.metadata["game"] = game_label
                
                print(f"    Transforming to graph documents (this may take a while)...")
                # Process in batches to avoid timeouts and API limits
                batch_size = 5
                for i in range(0, len(docs), batch_size):
                    batch = docs[i:i+batch_size]
                    print(f"      Processing batch {i//batch_size + 1}/{(len(docs)-1)//batch_size + 1}...")
                    graph_docs = transformer.convert_to_graph_documents(batch)
                    
                    for g_doc in graph_docs:
                        for node in g_doc.nodes:
                            node.properties["entity"] = entity_name
                            node.properties["game"] = game_label
                            # In newer versions, Node has 'type', not 'labels'
                            # We can set the type to our node_label
                            node.type = node_label
                        
                        for rel in g_doc.relationships:
                            rel.properties["entity"] = entity_name
                            rel.properties["game"] = game_label
                    
                    print(f"      Adding batch to Neo4j...")
                    graph.add_graph_documents(graph_docs, baseEntityLabel=node_label)
                    
                    # Link this batch to Root
                    link_query = f"""
                    MATCH (n {{entity: $entity, game: $game}})
                    WHERE n:{node_label} OR n:__Entity__
                    MERGE (root:RootEntity {{name: $entity, game: $game}})
                    SET root:{node_label}
                    WITH n, root
                    WHERE n <> root
                    MERGE (root)-[:HAS_INFORMATION {{entity: $entity, game: $game}}]->(n)
                    """
                    graph.query(link_query, {"entity": entity_name, "game": game_label})
                
                print(f"    Successfully added all batches for {entity_name} to Neo4j.")
                
            except Exception as e:
                print(f"    Error processing {filename}: {e}")

    # Export specific game to JSON
    export_to_json(game_key)

def export_to_json(game_key: str):
    game_label = GAME_CONFIG[game_key]["label"]
    output_file = f"{game_key}_graph_backup.json"
    print(f"Exporting {game_label} graph to {output_file}...")
    
    query = """
    MATCH (n {game: $game})
    OPTIONAL MATCH (n)-[r {game: $game}]->(m)
    RETURN n, r, m
    """
    results = graph.query(query, {"game": game_label})
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

async def main():
    parser = argparse.ArgumentParser(description="Populate Neo4j GraphRAG for Countrydle games.")
    parser.add_argument("--game", choices=["countries", "powiaty", "us_states", "wojewodztwa", "all"], default="all")
    args = parser.parse_args()

    if args.game == "all":
        for game_key in GAME_CONFIG.keys():
            try:
                await process_game(game_key)
            except Exception as e:
                print(f"Failed to process game {game_key}: {e}")
    else:
        await process_game(args.game)
    
    print("\nNeo4j GraphRAG Population Complete!")
    print("JSON backups created in the current directory.")
    print("To backup Neo4j database, run:")
    print("docker exec neo4j neo4j-admin database backup --to-path=/var/lib/neo4j/import neo4j")

if __name__ == "__main__":
    asyncio.run(main())
