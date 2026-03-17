"""Prompt assembly for note-grounded chat."""

from __future__ import annotations


def build_chat_messages(*, history: list[dict[str, str]], content: str, retrieved_chunks: list[dict[str, object]]) -> list[dict[str, str]]:
    """Build the grounded chat prompt."""

    context_lines = [
        f"[{index + 1}] {chunk['noteTitle']}: {chunk['snippet']}"
        for index, chunk in enumerate(retrieved_chunks)
    ]
    system_prompt = (
        "You answer strictly from the user's notes. "
        "If the notes do not contain the answer, say that clearly. "
        "When you use note content, mention the note title naturally."
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append(
        {
            "role": "user",
            "content": (
                f"Question: {content}\n\n"
                f"Relevant notes:\n{chr(10).join(context_lines) if context_lines else 'No indexed notes found.'}"
            ),
        }
    )
    return messages
