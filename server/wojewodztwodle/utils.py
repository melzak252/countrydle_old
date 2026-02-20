import os
import json
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Wojewodztwo, WojewodztwodleDay, User
from qdrant.utils import get_fragments_matching_question
from qdrant import COLLECTION_NAME
from schemas.wojewodztwodle import WojewodztwoQuestionCreate, WojewodztwoQuestionEnhanced
from db.repositories.wojewodztwo import WojewodztwoRepository


async def enhance_question(question: str) -> WojewodztwoQuestionEnhanced:
    system_prompt = """
You are an AI assistant for a game where players guess a Polish Voivodeship (Województwo) by asking True/False questions. 
Your task is to:

1. Receive a user's question.
2. Retrieve the meaning of the user's question.
3. Determine if it is a valid True/False question about a possible Polish Voivodeship.
4. Questions asking if the voivodeship is a specific one (e.g., "Is it Małopolskie?") are VALID.
5. If it's valid, then improve the question by making it more obvious about its intent.
6. If it's not valid, then provide an explanation why the question is not valid.

Instructions:
- The player may refer to the selected voivodeship in various ways, including:
    - Talking about themselves or referring to being in the voivodeship: "Am I ...?", "Do I ...?" etc.
    - Using "it/this/that": "Is it ...?", "Does it ...?", "Is this ...?", "Is that ...?" etc.
    - Using "the voivodeship" or "the province": "Is the voivodeship ...?", "Does the province ...?", etc.
    - Using "here" or "there": "is here ...?", "is there ...?", etc.
    - Using short forms: "in ...?", "is ...?" etc.
- Always respond in English.
- The improved question should always use the "the voivodeship" version of the question.

### Output Format
Answer with JSON format and nothing else. 
Use the specific format:
{
  "question": "Improved question if question is valid",
  "explanation": "Explanation if question is not valid",    
  "valid": true | false
}

### Examples
User's Question: Is it in the South?
Output: 
{
  "question": "Is the voivodeship located in the South?",
  "valid": true
}

User's Question: Is it Małopolskie?
Output: 
{
  "question": "Is the voivodeship Małopolskie?",
  "valid": true
}

User's Question: Tell me about its history
Output:
{
  "explanation": "This is not a True/False question.",
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

    return WojewodztwoQuestionEnhanced(
        original_question=question,
        valid=answer_dict["valid"],
        question=answer_dict.get("question", None),
        explanation=answer_dict.get("explanation", None),
    )


async def ask_question(
    question: WojewodztwoQuestionEnhanced,
    day_wojewodztwo: WojewodztwodleDay,
    user: User,
    session: AsyncSession,
) -> WojewodztwoQuestionCreate:

    fragments, question_vector = await get_fragments_matching_question(
        question.question, "wojewodztwo_id", day_wojewodztwo.wojewodztwo_id, "wojewodztwa", session
    )
    context = "\n[ ... ]\n".join(fragment.text for fragment in fragments)
    wojewodztwo: Wojewodztwo = await WojewodztwoRepository(session).get(day_wojewodztwo.wojewodztwo_id)

    system_prompt = f"""
You are an AI assistant in a game where players try to guess a Polish Voivodeship (Województwo) by asking True/False questions. 
Your task is to:
1. Receive a valid True/False question from the player.
2. Use the provided voivodeship and context to answer the question accurately.

Instructions:
- Base your answers primarily on the provided context. If the context does not contain enough information, use your general knowledge to provide the most accurate answer possible.
- If you cannot determine the answer even with general knowledge, set "answer" to null.
- Incorporate any relevant details from the provided context about the voivodeship into your explanations.
- If the question asks whether the voivodeship is a neighbor of itself, answer "true".
- Explanations should be provided before the answer.
- Answer should be consistent with the explanation.

### Voivodeship to Guess: {wojewodztwo.nazwa}
### Context: 
[...]
{context}
[...]

### Output Format
Answer with JSON format and nothing else. Use the specific format:
{{
    "explanation": "Your explanation for your answer.",
    "answer": true | false | null
}}
"""
    question_prompt = f"""Question: {question.question}"""

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
        answer_dict = json.loads(answer)
    except json.JSONDecodeError:
        print(answer)
        raise

    question_create = WojewodztwoQuestionCreate(
        user_id=user.id,
        day_id=day_wojewodztwo.id,
        original_question=question.original_question,
        valid=question.valid,
        question=question.question,
        answer=answer_dict["answer"],
        explanation=answer_dict["explanation"],
        context=context,
    )

    return question_create, question_vector
