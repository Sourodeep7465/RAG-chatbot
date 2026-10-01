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


def clean_context(text: str) -> str:
    """Clean context text to avoid model issues."""
    # Remove problematic characters
    text = text.replace("\ufffd", "'")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2026", "...")
    text = text.replace("\u00a0", " ")
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def generate_answer(query: str, chunks: list[dict]) -> str:
    """Generate an answer using Groq API."""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not found in .env file."

    # Filter out chunks that are too short (likely URL fragments)
    valid_chunks = [c for c in chunks if len(c['text']) > 100]

    if not valid_chunks:
        valid_chunks = chunks  # fallback to all chunks

    # Build context - use top 4 chunks, no truncation
    context_parts = []
    for i, chunk in enumerate(valid_chunks[:4], 1):
        context_parts.append(f"[Source {i}]\n{chunk['text']}")
    context = "\n\n".join(context_parts)

    # Clean context
    context = clean_context(context)

    # Truncate total context to avoid token limits
    if len(context) > 4000:
        context = context[:4000]

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
        if not answer or "could not find" in answer.lower():
            # Fallback: try with simpler prompt
            simple_prompt = f"Based on the following information, answer the question: {query}\n\n{context}\n\nAnswer:"
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": simple_prompt}],
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
