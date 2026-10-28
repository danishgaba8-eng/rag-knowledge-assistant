"""Unit tests for chunking, keyword search, fusion and access control (no LLM needed)."""

import numpy as np

from rag.config import ROLE_ACCESS
from rag.documents import chunk_document, parse_front_matter
from rag.retrieval import BM25, HybridRetriever, reciprocal_rank_fusion, tokenize

DOC = """---
title: Test Policy
department: HR
access: manager
---

# Test Policy

Intro text.

## First section

Alpha beta gamma.

## Second section

Delta epsilon.
"""


def test_front_matter():
    meta, body = parse_front_matter(DOC)
    assert meta == {"title": "Test Policy", "department": "HR", "access": "manager"}
    assert body.startswith("# Test Policy")


def test_chunks_carry_metadata_and_headings():
    chunks = chunk_document("test", DOC)
    assert [c.section for c in chunks] == ["First section", "Second section"]
    assert all(c.access == "manager" for c in chunks)
    assert chunks[0].text.startswith("Test Policy - First section")


def test_tokenize_keeps_codes_and_numbers():
    assert tokenize("Use HP-4820019377 and $0.42 rate") == ["use", "hp-4820019377", "0.42", "rate"]


def test_bm25_prefers_matching_doc():
    bm25 = BM25(["forklift certification renewal", "expense receipts and meals"])
    scores = bm25.scores("forklift renewal")
    assert scores[0] > scores[1] == 0


def test_rrf_rewards_agreement():
    fused = reciprocal_rank_fusion([[1, 2, 3], [2, 1, 3]])
    assert fused[1] == fused[2] > fused[3]


def test_access_filter_blocks_restricted_chunks():
    public = chunk_document("pub", DOC.replace("access: manager", "access: all"))
    secret = chunk_document("hr", DOC.replace("access: manager", "access: hr"))
    chunks = public + secret
    emb = np.eye(len(chunks), dtype=np.float32)
    retriever = HybridRetriever(chunks, emb)
    hits = retriever.search("alpha", emb[-1], ROLE_ACCESS["employee"], top_k=10)
    assert hits and all(h.chunk.access == "all" for h in hits)
    hits = retriever.search("alpha", emb[-1], ROLE_ACCESS["hr"], top_k=10)
    assert any(h.chunk.access == "hr" for h in hits)
