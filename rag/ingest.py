"""Build the search index: python -m rag.ingest"""

from .assistant import build_index
from .config import Settings

if __name__ == "__main__":
    build_index(Settings())
