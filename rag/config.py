"""Settings, read from environment variables (or a .env file)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Which document access levels each role may read.
ROLE_ACCESS = {
    "employee": {"all"},
    "manager": {"all", "manager"},
    "hr": {"all", "manager", "hr"},
}


@dataclass
class Settings:
    provider: str = field(default_factory=lambda: os.getenv("RAG_PROVIDER", "ollama"))
    docs_dir: Path = ROOT / "data" / "docs"
    index_dir: Path = ROOT / "data" / "index"

    # Ollama (local)
    ollama_url: str = field(default_factory=lambda: os.getenv("OLLAMA_URL", "http://localhost:11434"))
    ollama_chat_model: str = field(default_factory=lambda: os.getenv("OLLAMA_CHAT_MODEL", "llama3.2"))
    ollama_embed_model: str = field(default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"))

    # Azure OpenAI
    azure_endpoint: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    azure_api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    azure_api_version: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"))
    azure_chat_deployment: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", ""))
    azure_embed_deployment: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT", ""))

    # Retrieval
    top_k: int = 4
    candidates: int = 10
    # Below this cosine similarity for the best chunk, the assistant answers "not found"
    # without calling the LLM. Tuned with eval/run_eval.py.
    min_similarity: float = field(default_factory=lambda: float(os.getenv("RAG_MIN_SIMILARITY", "0.55")))
