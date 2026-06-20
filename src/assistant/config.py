from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = PROJECT_ROOT / "data" / "docs"
DB_PATH = PROJECT_ROOT / "data" / "company.db"
STORAGE_DIR = PROJECT_ROOT / "storage"
INDEX_PATH = STORAGE_DIR / "index.npz"
META_PATH = STORAGE_DIR / "chunks.json"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHAT_MODEL = "claude-sonnet-4-6"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
TOP_K = 4
MAX_STEPS = 6
