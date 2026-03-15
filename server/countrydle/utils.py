import os
import json
from typing import List, Tuple
from openai import OpenAI

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Country, CountrydleDay, User
from qdrant.utils import get_fragments_matching_question
import qdrant
from schemas.country import DayCountryDisplay
from schemas.countrydle import QuestionCreate, QuestionEnhanced
from db.repositories.country import CountryRepository


async def enhance_question(question: str) -> QuestionEnhanced:
    system_prompt = """
You are an expert Question Analyzer for a geography guessing game. Your goal is to process user questions into a structured format that facilitates accurate information retrieval.

### Your Core Responsibilities:
1. **Semantic Analysis**: Understand the true intent behind the user's question, regardless of language or phrasing.
2. **Validation**: Determine if the input is a valid True/False question about a country's attributes (geography, politics, culture, etc.).
3. **Simplification**: Rewrite the question into a clear, atomic, and standardized English sentence with "the country" as the subject.
4. **Intent & Information Mapping**: Explicitly define what the question is trying to verify and what specific data points are needed to answer it.

### Guidelines:
- **Language Agnostic**: The user might ask in any language. Always translate the meaning to English for the `question` field.
- **Entity Reference**: The user may refer to the target country in various ways:
    - Talking about themselves: "Am I ...?", "Do I ...?", "Am I located in ...?"
    - Using "it/this/that": "Is it ...?", "Does it ...?", "Is this ...?"
    - Using "the country": "Is the country ...?", "Does the country ...?"
- **Subject Consistency**: The simplified question MUST start with or focus on "the country" (e.g., "Is the country...", "Does the country...").
- **Atomic Intent**: If a question is compound, focus on the primary query (e.g., "Is the country located in Eurasia?" -> "Is the country located in Europe or Asia?").
- **Required Info**: Be specific about the data needed (e.g., "List of bordering countries", "Official currency", "GDP per capita").

### Output Format (Strict JSON):
{
  "question": "Simplified English T/F question",
  "intent": "Detailed description of the user's intention and what they are trying to find out",
  "required_info": "Specific data points needed from the database",
  "valid": true,
  "explanation": null
}
-- OR if invalid --
{
  "question": null,
  "intent": null,
  "required_info": null,
  "valid": false,
  "explanation": "Clear reason why the question is invalid (e.g., not a T/F question, gibberish)"
}

### Examples:
User: "Czy graniczy z Niemcami?"
Output: {"question": "Does the country border Germany?", "intent": "The user wants to verify if the target country shares a physical land border with Germany.", "required_info": "List of countries that share a land border with the target country", "valid": true, "explanation": null}

User: "Is it Poland?"
Output: {"question": "Is the country Poland?", "intent": "The user is making a direct guess to see if the target country is Poland.", "required_info": "The name of the country", "valid": true, "explanation": null}

User: "Is it Germany, Poland or France?"
Output: {"question": "Is the country one of the following: Germany, Poland, or France?", "intent": "The user is providing a list of countries and wants to know if the target country is one of them.", "required_info": "The name of the country", "valid": true, "explanation": null}

User: "Is it in Eurasia?"
Output: {"question": "Is the country located in Europe or Asia?", "intent": "The user is inquiring about the continental location of the country, specifically if it belongs to the combined landmass of Europe and Asia. This requires checking both Europe and Asia as potential continents.", "required_info": "The continent(s) where the country is located", "valid": true, "explanation": null}

User: "Tell me about the capital."
Output: {"question": null, "intent": null, "required_info": null, "valid": false, "explanation": "This is an open-ended request, not a True/False question."}
"""

    question_prompt = f"""User's Question: {question}"""

    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_prompt},
    ]
    model = os.getenv("QUIZ_MODEL")

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=prompts,
        response_format={"type": "json_object"},
        temperature=0.0,
        seed=42,
    )

    answer = response.choices[0].message.content

    try:
        answer_dict: dict = json.loads(answer)
    except json.JSONDecodeError:
        print(answer)
        raise

    return QuestionEnhanced(
        original_question=question,
        valid=answer_dict["valid"],
        question=answer_dict.get("question", None),
        intent=answer_dict.get("intent", None),
        required_info=answer_dict.get("required_info", None),
        explanation=answer_dict.get("explanation")
        or ("No explanation provided." if not answer_dict["valid"] else None),
    )


async def ask_question(
    question: QuestionEnhanced,
    day_country: CountrydleDay,
    user: User | None,
    session: AsyncSession,
) -> Tuple[QuestionCreate, List[float]]:

    fragments, question_vector = await get_fragments_matching_question(
        question.question,
        "country_id",
        day_country.country_id,
        "countries",
        session,
        limit=qdrant.COUNTRYDLE_CONTEXT_LIMIT,
    )
    context = "\n[ ... ]\n".join(fragment.text for fragment in fragments)
    country: Country = await CountryRepository(session).get(day_country.country_id)

    system_prompt = f"""
You are the 'Game Master' for Countrydle. Your task is to answer a True/False question about a specific country based on provided context and your general knowledge.

### Target Country: {country.name}
### Question Intent: {question.intent}
### Required Information: {question.required_info}

### Context Fragments:
{context}

### Your Instructions:
1. **Analyze the Context**: Look for specific facts in the provided context that directly confirm or deny the question.
2. **Use General Knowledge**: If the context is missing the specific fact, use your internal knowledge to provide an accurate answer.
3. **Handle Super-regions (e.g., Eurasia)**: If the question asks about a large landmass or super-region (like Eurasia, The Americas, Oceania), and the country is located in any part of that region (e.g., Europe or Asia for Eurasia), the answer must be `true`.
4. **Transcontinental Logic**: For countries spanning multiple continents (e.g., Turkey, Russia, Egypt, Kazakhstan), if the question asks if they are in either of those continents, the answer is `true`.
5. **Handle Uncertainty**: If the answer cannot be determined with high confidence, set `answer` to `null`.
6. **Special Rule (Self-Bordering)**: If asked if the country borders/neighbors [X], and the target country IS [X], the answer is ALWAYS `true`. Treat a country as bordering itself for the purpose of this game.
7. **Temporal Cutoff**: For any events or data from April 2024 onwards, set `answer` to `null`.
8. **Informative Explanations**: Write the `explanation` as factual information about the country that answers the question and provides details. Avoid starting with 'Yes' or 'No' or simply repeating the answer. The explanation should be an informative statement about the country that justifies the True/False answer (e.g., instead of 'Yes, it is in Europe', use '{country.name} is a country located in Southeastern Europe, bordering the Black Sea.').
9. **Handle Logical 'OR' and Lists**: If a question contains 'or' or provides a list of options (e.g., 'Is it in Europe or Asia?', 'Is it Poland, Germany, or France?'), the answer is `true` if the target country matches **at least one** of those options. Do not answer `false` just because it doesn't match all of them.

10. **User Perspective**: If the user refers to themselves as the country (e.g., "Am I in Europe?"), you should still answer about the country in the third person (e.g., "{country.name} is in Europe") to maintain a factual and informative tone.

### Output Format (Strict JSON):
{{
    "explanation": "Informative factual statement about the country.",
    "answer": true | false | null
}}
"""

    question_prompt = f"""User's Original Question: {question.original_question}
Simplified Question: {question.question}"""

    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_prompt},
    ]
    model = os.getenv("QUIZ_MODEL")

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=prompts,
        response_format={"type": "json_object"},
        temperature=0.0,
        seed=42,
    )

    answer = response.choices[0].message.content

    try:
        answer_dict = json.loads(answer)
    except json.JSONDecodeError:
        print(answer)
        raise

    question_create = QuestionCreate(
        user_id=user.id if user else None,
        day_id=day_country.id,
        original_question=question.original_question,
        valid=question.valid,
        question=question.question,
        answer=answer_dict.get("answer"),
        explanation=answer_dict.get("explanation") or "No explanation provided.",
        context=context,
    )

    return question_create, question_vector


async def give_guess(
    guess: str, daily_country: DayCountryDisplay, user: User, session: AsyncSession
):
    country: Country = await CountryRepository(session).get(daily_country.country_id)

    system_prompt = f"""
    You are the game master for a country guessing game. The player will guess a country, and you must determine if the guess is correct.

    Answering Guidelines:
        - true: If the player correctly guessed the country, including casual or abbreviated names (e.g., USA, Holland, Pol).
        - false: If the player's guess does not match the country.
        - null: If the guess is unclear or confusing.
    
    Answer guess True or False if you are fully confident of the answer.
    Answer guess NA if guess is confusing you.

    Country to Guess: {country.name} ({country.official_name})

    ### Task: 
    Use your best knowledge to determine if the player's guess is correct. Respond only in JSON format as follows:
    {{
        "answer": true | false | null,
    }}
    ### 
    
    ### Examples
    Country: Poland. Guess: Polska
    {{
        "answer": true
    }}
    
    Country: France. Guess: Franc
    {{
        "answer": true
    }}
    
    Country: United States of America. Guess: USA 
    {{
        "answer": true
    }}
    
    Country: Germany. Guess: Austria
    {{
        "answer": false
    }}
    
    Country: Australia. Guess: Austria
    {{
        "answer": false
    }}
    
    Country: France. Guess: Germany or France
    {{
        "answer": null
    }} # False because player tried to cheat. He can ask one guess at a time.
    """

    guess_prompt = f"Guess: {guess}"

    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": guess_prompt},
    ]
    model = os.getenv("QUIZ_MODEL")

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=prompts,
        response_format={"type": "json_object"},
        temperature=0.0,
        seed=42,
    )

    answer = response.choices[0].message.content

    try:
        answer_dict = json.loads(answer)
    except json.JSONDecodeError:
        print(answer)
        raise

    return answer_dict
