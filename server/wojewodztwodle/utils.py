import os
import json
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Wojewodztwo, WojewodztwodleDay, User
from utils.graph import graph_manager
from schemas.wojewodztwodle import (
    WojewodztwoQuestionCreate,
    WojewodztwoQuestionEnhanced,
)
from db.repositories.wojewodztwo import WojewodztwoRepository


async def enhance_question(question: str) -> WojewodztwoQuestionEnhanced:

    system_prompt = """
Jesteś asystentem AI w grze, w której gracze odgadują polskie województwo, zadając pytania Tak/Nie.
Twoim zadaniem jest:

1. Otrzymanie pytania użytkownika.
2. Zrozumienie znaczenia pytania użytkownika.
3. Określenie, czy jest to poprawne pytanie Tak/Nie dotyczące możliwego polskiego województwa.
4. Pytania o to, czy województwo jest konkretnym województwem (np. "Czy to Małopolskie?") są POPRAWNE.
5. Jeśli pytanie jest poprawne, ulepsz je, aby jego intencja była bardziej oczywista.
6. Jeśli pytanie nie jest poprawne, podaj wyjaśnienie, dlaczego nie jest ono poprawne.

Instrukcje:
- Gracz może odnosić się do wybranego województwa na różne sposoby, w tym:
    - Mówiąc o sobie lub odnosząc się do bycia w województwie: "Czy jestem ...?", "Czy mieszkam ...?" itp.
    - Używając "to/ten/tamten": "Czy to ...?", "Czy to województwo ...?" itp.
    - Używając "województwo": "Czy województwo ...?", "Czy to województwo ...?" itp.
    - Używając "tu" lub "tam": "czy tu jest ...?", "czy tam jest ...?" itp.
    - W różnych językach (głównie polskim lub angielskim).
- Zawsze odpowiadaj w języku polskim.
- Ulepszone pytanie musi zawsze mieć "województwo" jako podmiot zdania (np. "Czy województwo znajduje się na południu?").
- Sprawdź, czy pytanie ma sens i czy jest poprawnym zapytaniem o polskie województwo.

### Format wyjściowy
Odpowiedz w formacie JSON i niczym więcej.
Użyj określonego formatu:
{
  "question": "Ulepszone pytanie, jeśli jest poprawne",
  "explanation": "Wyjaśnienie, jeśli pytanie nie jest poprawne",
  "valid": true | false
}

### Przykłady
Pytanie użytkownika: Czy jest na południu?
Wyjście:
{
  "question": "Czy województwo znajduje się na południu?",
  "valid": true
}

Pytanie użytkownika: Czy to Małopolskie?
Wyjście:
{
  "question": "Czy województwo to Małopolskie?",
  "valid": true
}

Pytanie użytkownika: Opowiedz mi o jego historii
Wyjście:
{
  "explanation": "To nie jest pytanie typu Tak/Nie.",
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
    user: User | None,
    session: AsyncSession,
) -> WojewodztwoQuestionCreate:

    wojewodztwo: Wojewodztwo = await WojewodztwoRepository(session).get(
        day_wojewodztwo.wojewodztwo_id
    )
    
    # Use GraphRAG to get the answer
    answer_text = graph_manager.query_graph(
        question=question.question,
        entity_name=wojewodztwo.nazwa,
        game_key="wojewodztwa"
    )

    # We still use an LLM to format the answer into the expected JSON structure
    system_prompt = f"""
    Jesteś asystentem AI dla gry o nazwie Województwodle.
    Otrzymałeś odpowiedź z grafu wiedzy.
    Twoim zadaniem jest przekonwertowanie tej odpowiedzi na określony format JSON.

    ### Odpowiedź z grafu wiedzy:
    {answer_text}

    ### Docelowe Województwo: {wojewodztwo.nazwa}

    ### Format wyjściowy:
    {{
        "explanation": "Zwięzłe wyjaśnienie oparte na odpowiedzi z grafu.",
        "answer": true | false | null
    }}

    Zasady:
    - Jeśli odpowiedź z grafu potwierdza pytanie, ustaw "answer" na true.
    - Jeśli odpowiedź z grafu zaprzecza pytaniu, ustaw "answer" na false.
    - Jeśli odpowiedź z grafu to "Nie wiem" lub podobne, ustaw "answer" na null.
    - Wyjaśnienie powinno być pomocne, ale krótkie.
    - Zawsze odpowiadaj w języku polskim.
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

    question_create = WojewodztwoQuestionCreate(
        user_id=user.id if user else None,
        day_id=day_wojewodztwo.id,
        original_question=question.original_question,
        valid=question.valid,
        question=question.question,
        answer=answer_dict["answer"],
        explanation=answer_dict["explanation"],
        context=answer_text,
    )

    return question_create

