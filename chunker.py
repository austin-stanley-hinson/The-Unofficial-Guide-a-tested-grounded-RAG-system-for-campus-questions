"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"

    @property
    def category(self) -> str:
        """The filename prefix: admin, course, dining, housing, ... Used for filtering."""
        return self.source.split("_", 1)[0]


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks.

    Strategy for campus_life: one post is one chunk.

    Every post is a title line followed by a few short paragraphs, 178–549
    characters in total, and the title is often the only place the subject
    (which course, which hall) is named. So:

      - Paragraphs are packed whole, never cut mid-sentence, up to
        config.CHUNK_SIZE characters. At 600, every post in the corpus fits
        in one chunk.
      - If a post ever runs longer, it splits on a paragraph break and the
        title line is repeated at the top of every piece. That repeated title
        is the overlap: it carries the subject, where a window of borrowed
        characters would carry half a sentence.
      - A paragraph longer than CHUNK_SIZE on its own falls back to splitting
        on sentence ends.
    """
    size = config.CHUNK_SIZE
    chunks: list[Chunk] = []

    for doc in documents:
        paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]
        title, body = paragraphs[0], paragraphs[1:]
        room = size - len(title) - 2

        pieces: list[str] = []
        current = ""
        for para in _fit(body, room):
            candidate = f"{current}\n\n{para}" if current else para
            if current and len(candidate) > room:
                pieces.append(current)
                current = para
            else:
                current = candidate
        if current or not pieces:
            pieces.append(current)

        for index, piece in enumerate(pieces):
            text = f"{title}\n\n{piece}" if piece else title
            chunks.append(
                Chunk(
                    text=text,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def _fit(paragraphs: list[str], room: int) -> list[str]:
    """Break any paragraph longer than `room` on sentence ends, keep the rest."""
    import re

    out: list[str] = []
    for para in paragraphs:
        if len(para) <= room:
            out.append(para)
            continue
        current = ""
        for sentence in re.split(r"(?<=[.!?])\s+", para):
            candidate = f"{current} {sentence}" if current else sentence
            if current and len(candidate) > room:
                out.append(current)
                current = sentence
            else:
                current = candidate
        if current:
            out.append(current)
    return out


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
