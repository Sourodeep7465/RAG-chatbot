"""CLI script to test retrieval and answers."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.guardrails.classifier import should_refuse, get_refusal_message
from src.retrieve.retriever import Retriever, detect_scheme, rewrite_query
from src.generate.answer import generate_answer, append_citation


def ask(question: str, history: list[dict] = None, retrieval_only: bool = False) -> str:
    """Process a question through the full pipeline."""
    if history is None:
        history = []

    # Step 1: Guardrail check
    if should_refuse(question):
        return get_refusal_message(question)

    # Step 2: Rewrite query with memory
    standalone_query = rewrite_query(question, history)

    # Step 3: Detect scheme
    scheme = detect_scheme(standalone_query)

    # Step 4: Retrieve
    retriever = Retriever()
    chunks = retriever.retrieve(standalone_query, scheme=scheme)

    # Step 5: Check relevance
    if not retriever.is_relevant(chunks):
        return "I could not find this in the provided sources."

    # Step 6: Retrieval only mode
    if retrieval_only:
        output = f"Query: {standalone_query}\n"
        output += f"Scheme: {scheme or 'None detected'}\n"
        output += f"Retrieved {len(chunks)} chunks:\n\n"
        for i, chunk in enumerate(chunks, 1):
            output += f"--- Chunk {i} (similarity: {chunk['similarity']:.4f}) ---\n"
            output += f"Source: {chunk['source_url']}\n"
            output += f"Scheme: {chunk['scheme']}\n"
            output += f"Section: {chunk['section']}\n"
            output += f"Text: {chunk['text'][:200]}...\n\n"
        return output

    # Step 7: Generate answer
    answer = generate_answer(standalone_query, chunks)

    # Step 8: Append citation
    answer = append_citation(answer, chunks)

    return answer


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Mutual Fund FAQ RAG Chatbot")
    parser.add_argument("question", help="The question to ask")
    parser.add_argument("--retrieval-only", action="store_true", help="Only show retrieved chunks")
    args = parser.parse_args()

    result = ask(args.question, retrieval_only=args.retrieval_only)
    print(result)


if __name__ == "__main__":
    main()
