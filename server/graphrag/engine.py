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
        You are a strategic planner for a geography GraphRAG system.
        Your task is to:
        1. Analyze the user's question about a mystery country.
        2. Convert it into basic terms.
        3. Declare exactly what entities and relationships need to be checked in the graph database to answer this question.
        
        Output format: JSON
        {
            "basic_terms": "The question in simple English",
            "entities_to_check": ["List of entity types or names"],
            "relationships_to_check": ["List of relationship types"],
            "cypher_query": "A Cypher query to extract relevant context (optional but helpful)",
            "valid": true/false,
            "explanation": "If invalid, why?"
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
        Execute queries against KuzuDB to get context.
        """
        # This is a placeholder. In a real implementation, we would use the cypher_query
        # or build one based on entities_to_check.
        # For now, let's assume we query for the specific country's properties.
        
        try:
            # Example query: MATCH (c:Country {name: $name}) RETURN c.*
            # Note: Kuzu uses Cypher.
            query = f"MATCH (c:Country) WHERE c.name = '{country_name}' RETURN c.*"
            result = self.conn.execute(query)
            
            context_parts = []
            while result.has_next():
                row = result.get_next()
                # Format row as context string
                context_parts.append(str(row))
            
            return "\n".join(context_parts) if context_parts else "No specific graph context found."
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
