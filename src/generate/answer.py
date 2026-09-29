"""Generate answers using Groq API."""
import re
from typing import Optional

from groq import Groq

from src.config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPT = """You are a factual assistant for mutual fund information. Rules:
1. Use ONLY the provided context — never use outside knowledge.
2. Maximum 3 sentences.
3. No investment advice or opinions.
4. Do not add any links — the system will append the citation.
5. If the context doesn't contain the answer, say "I could not find this in the provided sources."
6. Be concise and factual."""


def strip_urls(text: str) -> str:
    """Remove any URLs from the generated text."""
    return re.sub(r'https?://\S+', '', text).strip()


def generate_answer(query: str, chunks: list[dict]) -> str:
    """Generate an answer using Groq API."""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not found in .env file."

    # Build context
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[Source {i}]\n{chunk['text']}")
    context = "\n\n".join(context_parts)

    # Build prompt
    user_prompt = f"""Context:
{context}

Question: {query}

Answer (max 3 sentences, facts only):"""

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.1,
        )
        answer = response.choices[0].message.content.strip()
        return strip_urls(answer)
    except Exception as e:
        return f"Error generating answer: {str(e)[:200]}"


def append_citation(answer: str, chunks: list[dict]) -> str:
    """Append exactly ONE citation to the answer."""
    if not chunks:
        return answer

    top_chunk = chunks[0]
    source_url = top_chunk.get("source_url", "")
    as_of_date = top_chunk.get("as_of_date", "")

    citation = f"\n\nSource: {source_url}"
    if as_of_date:
        citation += f" (Last updated: {as_of_date})"

    return answer + citation
