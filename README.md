# Mutual Fund FAQ RAG Chatbot

A facts-only RAG (Retrieval-Augmented Generation) chatbot that answers factual questions about selected HDFC Mutual Fund schemes using only official sources.

**Facts-only. No investment advice.**

## Scope

- **AMC:** HDFC Mutual Fund
- **Schemes:** HDFC Large Cap, HDFC Flexi Cap (formerly HDFC Equity Fund), HDFC ELSS Tax Saver, HDFC Small Cap, HDFC Balanced Advantage
- **All Direct-Growth plans only**
- **Sources:** hdfcfund.com, sebi.gov.in, amfi.com, amfiindia.com (official pages only)

## Architecture

```
Sources CSV → Fetch → Clean → Chunk → Embed → ChromaDB → Retrieve → Guardrail → Generate → Answer + Citation
```

- **Embeddings:** BAAI/bge-small-en-v1.5 (local, 384-dim)
- **Vector Store:** ChromaDB PersistentClient at `data/chroma`
- **Generation:** Groq API (llama-3.3-70b-versatile)
- **UI:** Streamlit
- **Config:** python-dotenv (.env)

## Setup

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd mf-faq-rag
   ```

2. **Create venv and install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Create .env file**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

4. **Build the corpus** (run in order)
   ```bash
   python -m src.ingest.fetcher       # Phase 1: Fetch sources
   python -m src.chunk.chunker       # Phase 2: Clean + chunk
   python -m src.embed.embedder      # Phase 3: Embed + store in ChromaDB
   ```

5. **Run the app**
   ```bash
   streamlit run app/main.py
   ```
   Open http://localhost:8501 in your browser.

## Test Questions

| Question | Expected Behavior |
|----------|-------------------|
| What is the expense ratio of HDFC Small Cap? | Answer with figure + one source link |
| What is the lock-in period for ELSS? | 3 years + source link |
| What is the minimum SIP for HDFC Large Cap? | Answer + source link |
| What is the exit load of HDFC Flexi Cap? | Answer + source link |
| What is the benchmark of HDFC Balanced Advantage? | Answer + source link |
| How to download capital gains statement? | Steps + source link |
| Should I invest in HDFC Small Cap? | Refusal + educational link |
| Who is the CEO of Tesla? | "I could not find this in the provided sources." |

## CLI Testing

```bash
# Test retrieval and answer
python scripts/ask.py "What is the expense ratio of HDFC Small Cap?"

# Test retrieval only (show chunks + scores)
python scripts/ask.py "What is the expense ratio of HDFC Small Cap?" --retrieval-only

# Verify ChromaDB persistence
python scripts/check_db.py

# Run guardrail tests
pytest tests/test_guardrails.py -v
```

## Known Limitations

- **Figures change over time:** The corpus is a snapshot. Expense ratios, exit loads, and other figures may have changed since the sources were fetched.
- **Only 5 schemes:** Only the 5 specified HDFC schemes are covered.
- **Sources snapshot date:** The corpus was built from sources fetched on 2026-09-30. Newer information may be available on the official websites.
- **hdfcfund.com blocking:** The AMC website blocks automated requests. The corpus was built from AMFI and SEBI pages that were accessible. HDFC-specific scheme data (expense ratio, exit load, etc.) may be limited.
- **No real-time data:** NAV, prices, and other real-time data are not available.
- **No investment advice:** The chatbot only provides factual information from official sources.

## Project Structure

```
mf-faq-rag/
├── app/
│   └── main.py              # Streamlit UI
├── data/
│   ├── raw/                 # Fetched raw text
│   ├── chunks/              # chunks.jsonl, chunks.txt, embeddings_preview.txt
│   ├── chroma/              # Persistent ChromaDB (git-ignored)
│   └── manifest/
│       └── sources.csv      # Source manifest
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   └── implementation.md
├── scripts/
│   ├── fetch_sources.py     # Phase 1: Fetch all URLs
│   ├── chunk_sources.py     # Phase 2: Clean + chunk
│   ├── embed_chunks.py      # Phase 3: Embed + store in ChromaDB
│   ├── check_db.py          # Phase 3: Verify persistence
│   └── ask.py               # Phase 5: CLI test
├── src/
│   ├── ingest/
│   │   └── fetcher.py       # URL fetching logic
│   ├── chunk/
│   │   └── chunker.py       # Text cleaning + chunking
│   ├── embed/
│   │   └── embedder.py      # Embedding + Chroma storage
│   ├── guardrails/
│   │   └── classifier.py    # Intent classification + refusal
│   ├── retrieve/
│   │   └── retriever.py     # Query rewrite + Chroma retrieval
│   └── generate/
│       └── answer.py        # Groq answer generation
├── tests/
│   └── test_guardrails.py   # Guardrail unit tests
├── .env                     # Secrets (git-ignored)
├── .env.example
├── .gitignore
├── requirements.txt
└── Problemstatement.txt
```

## Disclaimer

**Facts-only. No investment advice.** This chatbot provides factual information from official sources only. It does not provide investment advice, recommendations, or opinions. Always consult a qualified financial advisor before making investment decisions.
