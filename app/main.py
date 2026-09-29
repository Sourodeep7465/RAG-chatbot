"""Streamlit UI for Mutual Fund FAQ RAG Chatbot."""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st

from src.config import GROQ_API_KEY
from src.guardrails.classifier import should_refuse, get_refusal_message
from src.retrieve.retriever import Retriever, detect_scheme, rewrite_query
from src.generate.answer import generate_answer, append_citation


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "retriever" not in st.session_state:
        st.session_state.retriever = None


def get_retriever():
    """Get or create the retriever (singleton)."""
    if st.session_state.retriever is None:
        st.session_state.retriever = Retriever()
    return st.session_state.retriever


def process_question(question: str) -> str:
    """Process a question through the full pipeline."""
    # Step 1: Guardrail check
    if should_refuse(question):
        return get_refusal_message(question)

    # Step 2: Get conversation history (last 10 messages)
    history = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages

    # Step 3: Rewrite query with memory
    standalone_query = rewrite_query(question, history)

    # Step 4: Detect scheme
    scheme = detect_scheme(standalone_query)

    # Step 5: Retrieve
    retriever = get_retriever()
    chunks = retriever.retrieve(standalone_query, scheme=scheme)

    # Step 6: Check relevance
    if not retriever.is_relevant(chunks):
        return "I could not find this in the provided sources."

    # Step 7: Generate answer
    answer = generate_answer(standalone_query, chunks)

    # Step 8: Append citation
    answer = append_citation(answer, chunks)

    return answer


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Mutual Fund FAQ RAG Chatbot",
        page_icon="",
        layout="centered",
    )

    init_session_state()

    # Check for .env
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY not found. Please create a .env file with your Groq API key.")
        st.stop()

    # Welcome line
    st.title("Mutual Fund FAQ RAG Chatbot")
    st.markdown("**Ask factual questions about selected HDFC Mutual Fund schemes.**")

    # Disclaimer
    st.info("**Facts-only. No investment advice.**")

    # Example questions
    st.markdown("### Try these example questions:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("What is the expense ratio of HDFC Small Cap?"):
            st.session_state.example_question = "What is the expense ratio of HDFC Small Cap?"

    with col2:
        if st.button("What is the lock-in period for ELSS?"):
            st.session_state.example_question = "What is the lock-in period for ELSS?"

    with col3:
        if st.button("How to download capital gains statement?"):
            st.session_state.example_question = "How to download capital gains statement?"

    # Process example question if clicked
    if "example_question" in st.session_state:
        question = st.session_state.example_question
        del st.session_state.example_question

        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})

        # Process and add assistant message
        with st.spinner("Thinking..."):
            try:
                answer = process_question(question)
            except Exception as e:
                answer = f"Sorry, I encountered an error: {str(e)[:200]}"

        st.session_state.messages.append({"role": "assistant", "content": answer})

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process and display assistant message
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = process_question(prompt)
                except Exception as e:
                    answer = f"Sorry, I encountered an error: {str(e)[:200]}"

            st.markdown(answer)

        # Add assistant message to history
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # Clear chat button
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()
