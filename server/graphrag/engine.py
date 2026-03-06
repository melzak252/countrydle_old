import os
import json
from typing import List, Tuple, Optional
from openai import OpenAI
from .kuzu_client import get_connection
from schemas.countrydle import QuestionEnhanced, QuestionCreate
from db.models import CountrydleDay, User

class GraphRAGEngine:
    def __init__(self):
        self.client = OpenAI()
        self.model = os.getenv("QUIZ_MODEL", "gpt-4-turbo-preview")
        self.conn = get_connection()

    async def enhance_and_plan(self, question: str) -> dict:
        """
        Enhance the question and declare what needs to be checked in the graph.
        """
        system_prompt = """
        You are the 'Question Analyzer' for a geography GraphRAG system.
        Your goal is to decompose a user's question into its most atomic, searchable components.

        ### Task:
        1. **Simplify**: Rewrite the question into its most basic, atomic form (e.g., "Is it in the EU?" -> "Is the country a member of the European Union?").
        2. **Identify Concepts**: List the specific 'Concepts' (Organizations, Continents, Regions, Currencies, Languages, etc.) that must be retrieved from the graph to answer this.
        3. **Identify Properties**: List any direct country properties (population, area, capital) that are relevant.
        4. **Identify Relationships**: Determine the type of relationship to look for (e.g., "Borders", "Member Of", "Located In").
        5. **Validate**: Check if it's a valid True/False question about a country.

        ### Output Format (JSON):
        {
            "simplified_question": "Atomic version of the question",
            "required_concepts": ["List of specific concept names mentioned, e.g., 'Euro', 'Poland', 'NATO'"],
            "required_categories": ["List of categories to fetch all related items for, e.g., 'Currency', 'Language', 'River', 'Continent'"],
            "required_properties": ["population", "area", "capital", etc.],
            "relationship_types": ["BORDERS", "HAS_CONCEPT"],
            "valid": true/false,
            "explanation": "If invalid, why? If valid, brief reasoning."
        }

        ### Examples:
        User: "Does it use the Euro?"
        Output: {
            "simplified_question": "Does the country use the Euro currency?",
            "required_concepts": ["Euro"],
            "required_categories": ["Currency"],
            "required_properties": [],
            "relationship_types": ["HAS_CONCEPT"],
            "valid": true,
            "explanation": "Checking if Euro is a currency of the country."
        }

        User: "Does it border Poland and use the Euro?"
        Output: {
            "simplified_question": "Does the country border Poland and use the Euro currency?",
            "required_concepts": ["Poland", "Euro"],
            "required_properties": [],
            "relationship_types": ["BORDERS", "HAS_CONCEPT"],
            "valid": true,
            "explanation": "Checking physical border with Poland and currency concept."
        }
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Question: {question}"}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    async def extract_context(self, plan: dict, country_name: str) -> str:
        """
        Execute queries against KuzuDB to get context based on the plan.
        """
        context_parts = []
        
        try:
            # 1. Get Country Properties
            prop_query = f"MATCH (c:Country {{name: '{country_name}'}}) RETURN c.*"
            res = self.conn.execute(prop_query)
            if res.has_next():
                context_parts.append(f"Country Properties: {res.get_next()}")

            # 2. Get Specific Concepts from Plan
            for concept in plan.get("required_concepts", []):
                # Check if it's a border relationship (Country to Country)
                border_query = f"MATCH (a:Country {{name: '{country_name}'}})-[r:BORDERS]-(b:Country {{name: '{concept}'}}) RETURN b.name"
                res = self.conn.execute(border_query)
                if res.has_next():
                    context_parts.append(f"Border Fact: The country borders {concept}.")

                # Check generic concepts
                concept_query = f"MATCH (c:Country {{name: '{country_name}'}})-[r:HAS_CONCEPT]->(con:Concept {{name: '{concept}'}}) RETURN r.relationship, con.name"
                res = self.conn.execute(concept_query)
                while res.has_next():
                    row = res.get_next()
                    context_parts.append(f"Fact: {country_name} has relationship '{row[0]}' with {row[1]}.")

            # 3. Get all concepts for required categories (e.g., fetch ALL currencies if question is about currency)
            for category in plan.get("required_categories", []):
                cat_query = f"MATCH (c:Country {{name: '{country_name}'}})-[r:HAS_CONCEPT]->(con:Concept) WHERE con.category = '{category}' RETURN r.relationship, con.name"
                res = self.conn.execute(cat_query)
                cat_facts = []
                while res.has_next():
                    row = res.get_next()
                    cat_facts.append(f"{row[0]}: {row[1]}")
                if cat_facts:
                    context_parts.append(f"Category '{category}' facts for {country_name}: {', '.join(cat_facts)}")

            # 4. Get all neighbors if BORDERS is in plan but no specific country mentioned
            if "BORDERS" in plan.get("relationship_types", []) and not plan.get("required_concepts"):
                neighbors_query = f"MATCH (c:Country {{name: '{country_name}'}})-[:BORDERS]-(n:Country) RETURN n.name"
                res = self.conn.execute(neighbors_query)
                neighbors = []
                while res.has_next():
                    neighbors.append(res.get_next()[0])
                if neighbors:
                    context_parts.append(f"Neighbors: {', '.join(neighbors)}")

            return "\n".join(context_parts) if context_parts else "No specific graph context found for this query."
        except Exception as e:
            print(f"KuzuDB Query Error: {e}")
            return "Error extracting context from graph."

    async def ask_with_graph_context(
        self, 
        question_text: str, 
        context: str, 
        country_name: str
    ) -> Tuple[bool, str]:
        """
        Ask the LLM to answer the question based on graph context.
        """
        system_prompt = f"""
        You are an AI assistant for Countrydle.
        Answer the user's question about the country: {country_name}.
        Use the following graph-based context:
        {context}
        
        Answer only with True, False, or Null (if unknown).
        Provide a brief explanation.
        
        Output format: JSON
        {{
            "answer": true/false/null,
            "explanation": "..."
        }}
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {question_text}"}
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        return data.get("answer"), data.get("explanation", "No explanation provided.")

graph_rag_engine = GraphRAGEngine()
