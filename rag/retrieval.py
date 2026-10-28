"""Hybrid retrieval: BM25 keyword search + vector search, merged with reciprocal rank fusion."""

import math
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np

from .documents import Chunk

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)*")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from", "how",
    "i", "if", "in", "is", "it", "many", "much", "my", "of", "on", "or", "the", "to", "what",
    "when", "who", "with", "within", "you", "your",
}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


class BM25:
    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tokens = [tokenize(d) for d in docs]
        self.tf = [Counter(t) for t in self.tokens]
        self.avgdl = sum(len(t) for t in self.tokens) / max(len(self.tokens), 1)
        df = Counter(term for toks in self.tokens for term in set(toks))
        n = len(self.tokens)
        self.idf = {term: math.log(1 + (n - f + 0.5) / (f + 0.5)) for term, f in df.items()}

    def scores(self, query: str) -> np.ndarray:
        q = tokenize(query)
        out = np.zeros(len(self.tokens), dtype=np.float32)
        for i, tf in enumerate(self.tf):
            dl = len(self.tokens[i])
            for term in q:
                if term in tf:
                    f = tf[term]
                    out[i] += self.idf[term] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return out


def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> dict[int, float]:
    fused: dict[int, float] = {}
    for ranking in rankings:
        for rank, idx in enumerate(ranking):
            fused[idx] = fused.get(idx, 0.0) + 1.0 / (k + rank + 1)
    return fused


@dataclass
class Hit:
    chunk: Chunk
    similarity: float  # cosine similarity from the vector search
    fused_score: float


class HybridRetriever:
    def __init__(self, chunks: list[Chunk], embeddings: np.ndarray):
        self.chunks = chunks
        self.embeddings = embeddings
        self.bm25 = BM25([c.text for c in chunks])

    def search(self, query: str, query_vec: np.ndarray, allowed_access: set[str],
               top_k: int = 4, candidates: int = 10) -> list[Hit]:
        # Access control is applied before ranking, so restricted text never reaches the LLM.
        allowed = [i for i, c in enumerate(self.chunks) if c.access in allowed_access]
        if not allowed:
            return []
        sims = self.embeddings[allowed] @ query_vec
        kw = self.bm25.scores(query)[allowed]

        vec_rank = [allowed[i] for i in np.argsort(-sims)[:candidates]]
        kw_rank = [allowed[i] for i in np.argsort(-kw)[:candidates] if kw[i] > 0]
        fused = reciprocal_rank_fusion([vec_rank, kw_rank])

        sim_by_idx = dict(zip(allowed, sims.tolist()))
        best = sorted(fused, key=fused.get, reverse=True)[:top_k]
        return [Hit(self.chunks[i], sim_by_idx[i], fused[i]) for i in best]
