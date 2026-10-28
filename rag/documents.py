"""Load markdown documents with front matter and split them into section-level chunks."""

import re
from dataclasses import asdict, dataclass
from pathlib import Path

MAX_CHUNK_CHARS = 1200


@dataclass
class Chunk:
    id: str
    doc_id: str
    title: str
    section: str
    department: str
    access: str
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


def parse_front_matter(raw: str) -> tuple[dict, str]:
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, re.DOTALL)
    if not match:
        return {}, raw
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, raw[match.end():]


def _split_long(text: str, limit: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split oversized sections on paragraph boundaries."""
    if len(text) <= limit:
        return [text]
    parts, current = [], ""
    for para in text.split("\n\n"):
        if current and len(current) + len(para) + 2 > limit:
            parts.append(current.strip())
            current = ""
        current += para + "\n\n"
    if current.strip():
        parts.append(current.strip())
    return parts


def chunk_document(doc_id: str, raw: str) -> list[Chunk]:
    meta, body = parse_front_matter(raw)
    title = meta.get("title", doc_id)
    sections = re.split(r"^## +", body, flags=re.MULTILINE)
    chunks = []
    for i, section in enumerate(sections[1:], start=1):
        heading, _, content = section.partition("\n")
        for j, piece in enumerate(_split_long(content.strip())):
            chunks.append(Chunk(
                id=f"{doc_id}#{i}.{j}",
                doc_id=doc_id,
                title=title,
                section=heading.strip(),
                department=meta.get("department", ""),
                access=meta.get("access", "all"),
                # Title and heading go into the chunk text so both retrievers can match them.
                text=f"{title} - {heading.strip()}\n{piece}",
            ))
    return chunks


def load_chunks(docs_dir: Path) -> list[Chunk]:
    chunks = []
    for path in sorted(docs_dir.glob("*.md")):
        chunks.extend(chunk_document(path.stem, path.read_text(encoding="utf-8")))
    return chunks
