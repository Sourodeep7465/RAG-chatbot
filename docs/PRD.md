# Product Requirements Document: Mutual Fund FAQ RAG Chatbot

## 1. Problem

Investors in Indian mutual funds need quick, accurate answers to factual questions about their fund schemes (expense ratio, exit load, minimum SIP, lock-in period, riskometer, benchmark, how to download statements). Today this information is scattered across AMC websites, SEBI, and AMFI — often buried in PDFs and factsheets. There is no single, reliable, facts-only source that answers with proper citations.

## 2. Target Users

- Existing and prospective HDFC Mutual Fund investors who need quick factual answers
- Students and educators learning about mutual fund mechanics
- Class demo audience (professors, peers)

## 3. Goals

- Answer factual queries about 5 HDFC Mutual Fund schemes using **only official sources**
- Every answer includes **exactly ONE source link** from retrieved chunk metadata
- Answers are **max 3 sentences** and show the "as of / last updated" date when available
- Refuse advice/opinion/portfolio questions with a polite facts-only message + one educational link
- If retrieval finds no supporting passage, say it could not find it — **never guess**

## 4. Non-Goals

- No investment advice, recommendations, or opinions
- No real-time NAV or price data
- No third-party sources (Groww, ET Money, etc.)
- No production-grade scalability or authentication
- No support for non-HDFC schemes

## 5. Scope

### AMC
HDFC Mutual Fund (hdfcfund.com)

### Schemes (all Direct-Growth)
1. HDFC Large Cap Fund
2. HDFC Flexi Cap Fund (formerly HDFC Equity Fund)
3. HDFC ELSS Tax Saver Fund
4. HDFC Small Cap Fund
5. HDFC Balanced Advantage Fund

### Allowed Sources (publishers)
- hdfcfund.com
- sebi.gov.in
- amfi.com
- amfiindia.com

### Valid Query Types
- Expense ratio
- Exit load
- Minimum SIP
- Lock-in period (ELSS)
- Riskometer
- Benchmark
- How to download statements / capital-gains statement
- Other factual scheme attributes

## 6. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | Answers factual queries only: expense ratio, exit load, minimum SIP, lock-in (ELSS), riskometer, benchmark, how to download statements / capital-gains statement |
| FR2 | Every answer includes exactly ONE source link, taken from retrieved chunk metadata |
| FR3 | Answers are max 3 sentences and show the "as of / last updated" date of the source when available |
| FR4 | Refuses advice/opinion/portfolio questions ("should I buy/sell", "which is best") with a polite facts-only message plus one educational AMFI or SEBI link |
| FR5 | If retrieval finds no supporting passage, say it could not find it in the sources. Do not guess |
| FR6 | Sources: official pages only (hdfcfund.com, sebi.gov.in, amfi.com, amfiindia.com). 15-25 pages total. Third-party sites are NOT valid citations |
| FR7 | UI: welcome line, 3 clickable example questions, note "Facts-only. No investment advice." |
| FR8 | Conversation memory: last 10 messages used for follow-up questions |

## 7. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | Runs locally (no cloud deployment) |
| NFR2 | API key via .env (python-dotenv), never hardcoded or committed |
| NFR3 | Persistent vector store (ChromaDB at data/chroma) |
| NFR4 | Local embeddings (BAAI/bge-small-en-v1.5 via sentence-transformers) |
| NFR5 | Groq API for generation |
| NFR6 | Streamlit for UI |

## 8. Acceptance Criteria

1. User asks "What is the expense ratio of HDFC Small Cap?" → Answer with figure + one source link + as-of date
2. User asks "Should I invest in HDFC Small Cap?" → Polite refusal + one AMFI/SEBI educational link
3. User asks "Who is the CEO of Tesla?" → "I could not find this in the sources."
4. User asks "What is the exit load?" (follow-up) → Correctly resolves scheme from conversation memory
5. Every answer has exactly one clickable source link
6. No answer exceeds 3 sentences
7. No third-party URLs appear in any citation
