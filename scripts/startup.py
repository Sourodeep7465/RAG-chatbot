"""
Bulletproof startup script for Render deployment.
Handles all edge cases and provides clear error messages.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("=" * 60)
    print("MF FAQ RAG Chatbot — Starting up")
    print("=" * 60)

    # Step 1: Check Python environment
    print(f"Python: {sys.version}")

    # Step 2: Check ChromaDB
    from src.config import CHROMA_DIR, CHROMA_COLLECTION
    print(f"ChromaDB path: {CHROMA_DIR}")
    print(f"ChromaDB exists: {CHROMA_DIR.exists()}")

    if not CHROMA_DIR.exists():
        print("ERROR: ChromaDB directory not found!")
        print("Make sure data/chroma/ is committed to the repo.")
        sys.exit(1)

    try:
        import chromadb
        from chromadb.config import Settings
        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = client.get_collection(CHROMA_COLLECTION)
        count = collection.count()
        print(f"ChromaDB OK: {count} chunks loaded")
    except Exception as e:
        print(f"ERROR: ChromaDB failed to load: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 3: Check Groq API key
    from src.config import GROQ_API_KEY, GROQ_MODEL
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY not set!")
        print("Add it in Render dashboard > Environment Variables")
        sys.exit(1)
    print(f"Groq API: configured (model={GROQ_MODEL})")

    # Step 4: Pre-download embedding model (prevents health check timeout)
    from src.config import EMBED_MODEL
    print(f"Pre-downloading embedding model: {EMBED_MODEL}")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(EMBED_MODEL)
        print(f"Embedding model ready: {EMBED_MODEL}")
    except Exception as e:
        print(f"ERROR: Failed to load embedding model: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 5: Get port from environment
    port = int(os.getenv("PORT", "8501"))
    print(f"Port: {port}")

    # Step 5: Start Streamlit
    print("=" * 60)
    print("Starting Streamlit server...")
    print("=" * 60)

    # Use subprocess to start streamlit (more reliable than bootstrap)
    import subprocess
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app/main.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.fileWatcherType", "none",
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(project_root))
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
