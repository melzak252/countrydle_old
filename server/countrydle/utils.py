import os
import json
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Country, CountrydleDay, User
from utils.graph import graph_manager
from schemas.country import DayCountryDisplay
from schemas.countrydle import QuestionCreate, QuestionEnhanced
from db.repositories.country import CountryRepository


async def enhance_question(question: str) -> QuestionEnhanced:

    system_prompt = """
You are an AI assistant for a game where players guess a country by asking True/False questions. 
Your task is to:

1. Receive a user's question.
2. Retrieve the meaning of the user's question.
3. Determine if it is a valid True/False question about possible country.
4. Questions asking if the country is a specific country (e.g., "Is it Poland?") are VALID.
5. If It's valid then improve the question by make it more obvious about its intent.
6. If It's not valid then provide an explanation why the question is not valid.

Instructions:
- The player may refer to the selected country in various ways, including:
    - Talking about themselves or referring to being in the country: "Am I ...?", "Do I ...?" etc.
    - Using "it/this/that": "Is it ...?", "Does it ...?", "Is this ...?", "Is that ...?" etc.
    - Using "the country": "Is the country ...?", "Does the country ...?", "Is that country ...?" etc.
    - Using "here" or "there": "is here ...?", "is there ...?", etc.
    - Using short forms: "in ...?", "is ...?" etc.
    - In different languages.
- Always respond in English.
- The improved question must always have "the country" as the subject of the sentence.
- Check if the question makes sense and is a valid query about a country.


### Output Format
Answer with JSON format and nothing else. 
Use the specific format:
{
  "question": "Improved question if question is valid",
  "explanation": "Explanation if question is not valid",    
  "valid": true | false
}

### Examples
User's Question: Is it in Europe?
Output: 
{
  "question": "Is the country located in Europe?",
  "valid": true
}

User's Question: in Europe
Output: 
{
  "question": "Is the country located in Europe?",
  "valid": true
}

User's Question: Czy w Azji?
Output: 
{
  "question": "Is the country located in Asia?",
  "valid": true
}

User's Question: Tell me about its history
Output:
{
  "explanation": "This is not a True/False question.",
  "valid": false
}

User's Question: Is it seychelles?
{
  "question": "Is the country Seychelles?",
  "valid": true,
}

User's Question: Is this island/s country
{
  "question": "Is the country an island nation?",
  "valid": true
}

User's Question: "asdfghjkl"
{
  "explanation": "The input is gibberish and not a valid True/False question.",
  "valid": false
}
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
        explanation=answer_dict.get("explanation", None),
    )


async def ask_question(
    question: QuestionEnhanced,
    day_country: CountrydleDay,
    user: User | None,
    session: AsyncSession,
) -> QuestionCreate:

    country: Country = await CountryRepository(session).get(day_country.country_id)
    
    # Use GraphRAG to get the answer
    answer_text = graph_manager.query_graph(
        question=question.question,
        entity_name=country.name,
        game_key="countries"
    )

    # We still use an LLM to format the answer into the expected JSON structure
    # and ensure it's a clean True/False/Null response.
    system_prompt = f"""
    You are an AI assistant for a game called Countrydle.
    You have been provided with an answer from a knowledge graph.
    Your task is to convert this answer into a specific JSON format.

    ### Knowledge Graph Answer:
    {answer_text}

    ### Target Country: {country.name}

    ### Output Format:
    {{
        "explanation": "A concise explanation based on the graph answer.",
        "answer": true | false | null
    }}

    Rules:
    - If the graph answer confirms the question, set "answer" to true.
    - If the graph answer denies the question, set "answer" to false.
    - If the graph answer is "I don't know" or similar, set "answer" to null.
    - The explanation should be helpful but brief.
    """
    
    model = os.getenv("QUIZ_MODEL")
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt}],
        response_format={"type": "json_object"},
    )

    answer_json = response.choices[0].message.content
    answer_dict = json.loads(answer_json)

    question_create = QuestionCreate(
        user_id=user.id if user else None,
        day_id=day_country.id,
        original_question=question.original_question,
        valid=question.valid,
        question=question.question,
        answer=answer_dict["answer"],
        explanation=answer_dict["explanation"],
        context=answer_text, # Store the graph output as context
    )

    return question_create



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
    )

    answer = response.choices[0].message.content

    try:
        answer_dict = json.loads(answer)
    except json.JSONDecodeError:
        print(answer)
        raise

    return answer_dict
