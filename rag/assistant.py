"""The knowledge assistant: build or load the index, retrieve, and answer with citations."""

import json
import re
from dataclasses import dataclass

import numpy as np

from .config import ROLE_ACCESS, Settings
from .documents import Chunk, load_chunks
from .providers import get_provider
from .retrieval import Hit, HybridRetriever

NOT_FOUND = "I couldn't find this in the company documents I have access to."

SYSTEM_PROMPT = """You are the internal knowledge assistant for Harbor & Pine Logistics.
Answer ONLY from the numbered context passages. Rules:
- Cite every fact with the passage number in square brackets, e.g. [1] or [2][3].
- If a passage answers the question, even partly, answer from it.
- Only if no passage is relevant to the question, reply with exactly: NOT_FOUND
- Do not use outside knowledge and do not guess numbers, dates or names.
- Keep answers short: 1 to 4 sentences.

Example answer: "Claims above $1,000 also need Finance Director approval [2]."
"""


@dataclass
class Answer:
    text: str
    sources: list[Hit]
    found: bool


def build_index(settings: Settings) -> None:
    provider = get_provider(settings)
    chunks = load_chunks(settings.docs_dir)
    embeddings = provider.embed_documents([c.text for c in chunks])
    settings.index_dir.mkdir(parents=True, exist_ok=True)
    np.save(settings.index_dir / "embeddings.npy", embeddings)
    (settings.index_dir / "chunks.json").write_text(
        json.dumps({"provider": provider.name, "chunks": [c.to_dict() for c in chunks]}, indent=2),
        encoding="utf-8",
    )
    print(f"Indexed {len(chunks)} chunks from {settings.docs_dir} with {provider.name}")


class KnowledgeAssistant:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.provider = get_provider(self.settings)
        meta = json.loads((self.settings.index_dir / "chunks.json").read_text(encoding="utf-8"))
        chunks = [Chunk(**c) for c in meta["chunks"]]
        embeddings = np.load(self.settings.index_dir / "embeddings.npy")
        self.retriever = HybridRetriever(chunks, embeddings)

    def retrieve(self, question: str, role: str = "employee") -> list[Hit]:
        return self.retriever.search(
            question,
            self.provider.embed_query(question),
            ROLE_ACCESS[role],
            top_k=self.settings.top_k,
            candidates=self.settings.candidates,
        )

    def ask(self, question: str, role: str = "employee") -> Answer:
        hits = self.retrieve(question, role)
        # Cheap guardrail: if nothing is even close, don't ask the LLM to improvise.
        if not hits or max(h.similarity for h in hits) < self.settings.min_similarity:
            return Answer(NOT_FOUND, [], False)

        context = "\n\n".join(f"[{i}] ({h.chunk.title} > {h.chunk.section})\n{h.chunk.text}"
                              for i, h in enumerate(hits, start=1))
        reply = self.provider.chat(SYSTEM_PROMPT, f"Context:\n{context}\n\nQuestion: {question}")

        if "NOT_FOUND" in reply:
            return Answer(NOT_FOUND, [], False)
        cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", reply) if 1 <= int(n) <= len(hits)})
        # If the model forgot to cite, fall back to the top-ranked passage.
        sources = [hits[n - 1] for n in cited] or hits[:1]
        return Answer(reply, sources, True)
