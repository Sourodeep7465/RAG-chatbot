# Implementation Plan

## Phase 0: Setup

**Goal:** Create venv, install dependencies, set up config loader and repo skeleton.

**Files to create:**
- `.venv/` (virtual environment)
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `src/config.py`

**Steps:**
1. Create venv: `python -m venv .venv`
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env.example` with placeholder values
4. Create `.gitignore` with `.env`, `.venv/`, `__pycache__/`, `data/chroma/`
5. Create `src/config.py` to load config from .env

**Done when:** `.venv` exists, `pip install` succeeds, `src/config.py` loads without errors.

---

## Phase 1: Corpus + Ingestion

**Goal:** Build `data/manifest/sources.csv` with 15-25 official URLs, fetch each URL, save raw text to `data/raw/`, log failures.

**Files to create:**
- `data/manifest/sources.csv`
- `src/ingest/fetcher.py`
- `data/raw/*.txt` (fetched content)

**Steps:**
1. Create `data/manifest/sources.csv` with columns: url, scheme, doc_type, publisher, fetched_at, status, notes
2. Add 15-25 official URLs from hdfcfund.com, sebi.gov.in, amfi.com, amfiindia.com
3. Write `src/ingest/fetcher.py` to fetch each URL and save to `data/raw/<slug>.txt`
4. Run `python -m src.ingest.fetcher`
5. Check `sources.csv` for statuses

**Done when:** `data/raw/` has files, `sources.csv` has statuses, failures are listed.

---

## Phase 2: Cleaning + Chunking

**Goal:** Clean raw text, chunk per architecture rules, write to `data/chunks/chunks.jsonl` and `data/chunks/chunks.txt`.

**Files to create:**
- `src/chunk/chunker.py`
- `data/chunks/chunks.jsonl`
- `data/chunks/chunks.txt`

**Steps:**
1. Write `src/chunk/chunker.py` with clean_text(), extract_as_of_date(), chunk_text() functions
2. Run `python -m src.chunk.chunker`
3. Check `data/chunks/chunks.txt` for readable chunks with metadata

**Done when:** `data/chunks/chunks.txt` is readable, chunks have metadata (chunk_id, source_url, scheme, doc_type, section, as_of_date).

---

## Phase 3: Embeddings + ChromaDB

**Goal:** Embed chunks with BAAI/bge-small-en-v1.5, store in ChromaDB, write embeddings preview, create check_db.py.

**Files to create:**
- `src/embed/embedder.py`
- `data/chunks/embeddings_preview.txt`
- `scripts/check_db.py`
- `data/chroma/` (ChromaDB persistent store)

**Steps:**
1. Write `src/embed/embedder.py` to embed chunks and store in ChromaDB
2. Run `python -m src.embed.embedder`
3. Check `data/chunks/embeddings_preview.txt` for chunk_id, first 8 dims, vector length
4. Write `scripts/check_db.py` to verify persistence
5. Run `python scripts/check_db.py` in a fresh process
6. Confirm `data/chroma` is git-ignored

**Done when:** `check_db.py` shows the same count after restarting terminal, `embeddings_preview.txt` has all chunks.

---

## Phase 4: Guardrails

**Goal:** Build rule-based intent classifier, refusal template, educational links, and unit tests.

**Files to create:**
- `src/guardrails/classifier.py`
- `tests/test_guardrails.py`

**Steps:**
1. Write `src/guardrails/classifier.py` with classify_intent(), should_refuse(), get_refusal_message()
2. Write `tests/test_guardrails.py` with 20+ test cases (10 refuse, 10 allow, tricky phrasing)
3. Run `pytest tests/test_guardrails.py -v`

**Done when:** All 24 guardrail tests pass.

---

## Phase 5: Retrieval + Generation

**Goal:** Build retriever with scheme detection and query rewriting, Groq answer generation, CLI script.

**Files to create:**
- `src/retrieve/retriever.py`
- `src/generate/answer.py`
- `scripts/ask.py`

**Steps:**
1. Write `src/retrieve/retriever.py` with detect_scheme(), rewrite_query(), Retriever class
2. Write `src/generate/answer.py` with generate_answer(), append_citation()
3. Write `scripts/ask.py` CLI script
4. Test with 8 test questions

**Done when:** All 8 test questions behave correctly, every answer has exactly one link.

---

## Phase 6: Streamlit UI

**Goal:** Build Streamlit app with welcome line, 3 example buttons, disclaimer, chat with 10-message memory.

**Files to create:**
- `app/main.py`

**Steps:**
1. Write `app/main.py` with Streamlit UI
2. Run `streamlit run app/main.py`
3. Test example buttons, follow-up questions, clear chat

**Done when:** App opens on localhost, example buttons work, follow-up questions resolve correctly.

---

## Phase 7: Final

**Goal:** Write README, verify git status, commit.

**Files to create:**
- `README.md`

**Steps:**
1. Write `README.md` with run steps, test questions, known limitations
2. Verify `git status` shows no `.env` and no `data/chroma`
3. Commit with clear message
4. Show commit list and `git remote -v`

**Done when:** README exists, git status is clean, commit is made.
