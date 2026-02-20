from typing import List
from openai import OpenAI


def get_embedding(text: str, model: str) -> List[float]:
    client = OpenAI()
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def get_bulk_embedding(texts: List[str], model: str) -> List[List[float]]:
    client = OpenAI()
    texts = [text.replace("\n", " ") for text in texts]
    response = client.embeddings.create(input=texts, model=model)
    return [data.embedding for data in response.data]
