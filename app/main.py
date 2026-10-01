"""Streamlit UI for Mutual Fund FAQ RAG Chatbot — Grow-inspired theme."""
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


# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MF FAQ — HDFC Mutual Fund Chatbot",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS (Grow-inspired theme) ───────────────────────────────────────
st.markdown("""
<style>
    /* Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 900px;
    }

    /* Header */
    .app-header {
        background: linear-gradient(135deg, #00D09C 0%, #00B894 50%, #00A383 100%);
        border-radius: 16px;
        padding: 2rem 2rem 1.5rem 2rem;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 4px 20px rgba(0, 208, 156, 0.3);
    }

    .app-header h1 {
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        color: white;
        letter-spacing: -0.5px;
    }

    .app-header p {
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
        opacity: 0.95;
        color: white;
    }

    /* Disclaimer badge */
    .disclaimer-badge {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border: 1px solid #FFB74D;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .disclaimer-badge span {
        font-size: 0.85rem;
        font-weight: 600;
        color: #E65100;
    }

    /* Example question buttons */
    .example-btn {
        background: white;
        border: 2px solid #E0E0E0;
        border-radius: 12px;
        padding: 1rem;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;
        height: 100%;
    }

    .example-btn:hover {
        border-color: #00D09C;
        background: #F0FFF9;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 208, 156, 0.15);
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    [data-testid="stChatMessage"][data-role="user"] {
        background: #F5F5F5;
        border: 1px solid #E0E0E0;
    }

    [data-testid="stChatMessage"][data-role="assistant"] {
        background: #F0FFF9;
        border: 1px solid #B2DFDB;
    }

    /* Source citation */
    .source-citation {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-top: 0.75rem;
        font-size: 0.85rem;
    }

    .source-citation a {
        color: #00D09C;
        text-decoration: none;
        font-weight: 600;
    }

    .source-citation a:hover {
        text-decoration: underline;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #FAFAFA;
        border-right: 1px solid #E0E0E0;
    }

    .sidebar-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #E0E0E0;
    }

    .sidebar-card h3 {
        font-size: 0.9rem;
        font-weight: 700;
        color: #333;
        margin: 0 0 0.5rem 0;
    }

    .sidebar-card p {
        font-size: 0.8rem;
        color: #666;
        margin: 0;
    }

    /* Scheme tags */
    .scheme-tag {
        display: inline-block;
        background: #E8F5E9;
        color: #2E7D32;
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.25rem;
    }

    /* Clear chat button */
    .clear-btn {
        background: white;
        border: 2px solid #E0E0E0;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        font-weight: 600;
        color: #666;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
    }

    .clear-btn:hover {
        border-color: #FF5252;
        color: #FF5252;
        background: #FFF5F5;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 12px;
        border: 2px solid #E0E0E0;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #00D09C;
    }

    /* Section title */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #333;
        margin: 1.5rem 0 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Spinner */
    [data-testid="stSpinner"] {
        color: #00D09C !important;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "retriever" not in st.session_state:
        st.session_state.retriever = None


def get_retriever():
    """Get or create the retriever (singleton)."""
    if st.session_state.retriever is None:
        with st.spinner("Loading models..."):
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


def render_sidebar():
    """Render the sidebar with scheme info and stats."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #00D09C; margin: 0;">MF FAQ</h2>
            <p style="color: #666; font-size: 0.8rem; margin: 0.25rem 0 0 0;">HDFC Mutual Fund Chatbot</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Supported schemes
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("<h3>Supported Schemes</h3>", unsafe_allow_html=True)
        st.markdown(
            '<span class="scheme-tag">HDFC Large Cap</span>'
            '<span class="scheme-tag">HDFC Flexi Cap</span>'
            '<span class="scheme-tag">HDFC ELSS Tax Saver</span>'
            '<span class="scheme-tag">HDFC Small Cap</span>'
            '<span class="scheme-tag">HDFC Balanced Advantage</span>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Data sources
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("<h3>Data Sources</h3>", unsafe_allow_html=True)
        st.markdown(
            "<p>hdfcfund.com<br>sebi.gov.in<br>amfiindia.com</p>",
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Stats
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("<h3>About</h3>", unsafe_allow_html=True)
        st.markdown(
            "<p>This chatbot answers factual questions about HDFC Mutual Fund schemes using official sources only. "
            "It does not provide investment advice.</p>",
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Clear chat button
        if st.button("Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()


def render_header():
    """Render the app header."""
    st.markdown("""
    <div class="app-header">
        <h1>Mutual Fund FAQ Chatbot</h1>
        <p>Ask factual questions about selected HDFC Mutual Fund schemes</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-badge">
        <span>Facts-only. No investment advice.</span>
    </div>
    """, unsafe_allow_html=True)


def render_example_questions():
    """Render clickable example questions."""
    st.markdown('<div class="section-title">Try these questions</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    examples = [
        ("What is the expense ratio of HDFC Small Cap?", "Expense Ratio"),
        ("What is the lock-in period for ELSS?", "ELSS Lock-in"),
        ("How to download capital gains statement?", "Capital Gains"),
    ]

    for col, (question, label) in zip([col1, col2, col3], examples):
        with col:
            if st.button(label, type="secondary", use_container_width=True):
                st.session_state.example_question = question


def render_chat():
    """Render the chat interface."""
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Process example question if clicked
    if "example_question" in st.session_state:
        question = st.session_state.example_question
        del st.session_state.example_question

        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})

        # Process and add assistant message
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = process_question(question)
                except Exception as e:
                    answer = f"Sorry, I encountered an error: {str(e)[:200]}"
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask a question about HDFC mutual funds..."):
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
        st.rerun()


def main():
    """Main Streamlit app."""
    init_session_state()

    # Check for .env
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY not found. Please create a .env file with your Groq API key.")
        st.stop()

    # Render UI
    render_sidebar()
    render_header()
    render_example_questions()
    render_chat()


if __name__ == "__main__":
    main()
