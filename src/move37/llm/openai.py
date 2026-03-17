"""OpenAI client and model calls."""

from __future__ import annotations

import os

from openai import OpenAI


class Move37OpenAIClient:
    """Encapsulate OpenAI chat and embedding calls."""

    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.embedding_model = os.environ.get("MOVE37_EMBEDDING_MODEL", "text-embedding-3-large")
        self.answer_model = os.environ.get("MOVE37_CHAT_MODEL", "gpt-4.1-mini")

    def embed_one(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.embedding_model, input=text)
        return list(response.data[0].embedding)

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.embedding_model, input=texts)
        return [list(item.embedding) for item in response.data]

    def chat(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.answer_model,
            messages=messages,
        )
        return response.choices[0].message.content or "I could not generate a response."
