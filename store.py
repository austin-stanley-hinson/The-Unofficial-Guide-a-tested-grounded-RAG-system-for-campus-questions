"""
Stages 3 and 4 of the pipeline: embedding chunks and retrieving them.

Three things in here are worth knowing about, because they'd quietly break the
rest of the project if they were wrong:

1. The Chroma collection is created with cosine distance, explicitly. Chroma
   defaults to squared L2, and the 0.6 threshold the course uses is calibrated
   against cosine. Getting this wrong makes every distance number meaningless.

2. `search` returns the distance alongside each chunk. Milestone 4 has you
   compare distances, so they have to be visible.

3. The embedding model is the one Chroma bundles, not one loaded through
   `sentence-transformers`. It is the same model — `all-MiniLM-L6-v2`, 384
   dimensions — but it arrives as an ONNX build from Chroma's own CDN, so the
   install needs neither PyTorch nor a reachable Hugging Face. See `_embedder`.
"""

import os
import re
import shutil
from dataclasses import dataclass

# Must be set BEFORE chromadb is imported. Without it, some Chroma versions
# print "Failed to send telemetry event ..." on every single call — which looks
# exactly like a real error, isn't one, and cost a previous cohort a lot of
# confused help-channel messages.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb  # noqa: E402

import config
from chunker import Chunk


@dataclass
class Result:
    """One retrieved chunk and how far it was from the question."""

    text: str
    source: str
    label: str
    distance: float   # LOWER IS BETTER. 0.3 is close, 0.9 is unrelated.
    produced_by: str


_model = None

# The model Chroma bundles. Anything else in config.EMBEDDING_MODEL means
# "fetch that one from Hugging Face instead" — see `_embedder`.
BUNDLED_MODEL = "all-MiniLM-L6-v2"


class _OnnxEmbedder:
    """
    Chroma's built-in embedder, wrapped to look like the other two.

    Chroma's embedding functions are called directly and hand back numpy
    arrays. The rest of this file wants `.encode(texts)`, so the adapter lives
    here rather than making every caller care which embedder it got.
    """

    def __init__(self):
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        self._ef = ONNXMiniLM_L6_V2()

    def encode(self, texts, show_progress_bar: bool = False):
        return [vector.tolist() for vector in self._ef(list(texts))]


def _sentence_transformer(name: str):
    """
    The escape hatch: any model that isn't the bundled one.

    Unit 2's "try a second embedding model" stretch option comes through here,
    and so does anything you set `EMBEDDING_MODEL` to. This path *does* need
    `sentence-transformers` and a reachable Hugging Face, neither of which the
    default install has — which is the whole point of the default install.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            f"config.EMBEDDING_MODEL is set to {name!r}, which isn't the model "
            f"Chroma bundles ({BUNDLED_MODEL!r}), so it has to be downloaded "
            f"from Hugging Face.\n"
            f"Install the optional dependency first:\n"
            f"    pip install 'sentence-transformers>=3.4,<3.5'\n"
            f"Or set EMBEDDING_MODEL back to {BUNDLED_MODEL!r}."
        ) from exc

    return SentenceTransformer(name)


def _embedder():
    """
    Load the embedding model once and keep it.

    First call is slow — it downloads about 80 MB. That's why setup happens
    before class.
    """
    global _model

    if _model is not None:
        return _model

    # Used only by this repo's own smoke test, which runs where no model can be
    # downloaded at all. Never set this yourself.
    if os.getenv("AI201_FAKE_EMBEDDINGS") == "1":
        from _smoke_embedder import FakeEmbedder

        _model = FakeEmbedder()
    elif config.EMBEDDING_MODEL == BUNDLED_MODEL:
        _model = _OnnxEmbedder()
    else:
        _model = _sentence_transformer(config.EMBEDDING_MODEL)

    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """Turn text into vectors. Runs on your machine, costs no API quota."""
    vectors = _embedder().encode(texts, show_progress_bar=False)
    # sentence-transformers and the smoke stand-in return something with a
    # .tolist(); _OnnxEmbedder has already done that conversion itself.
    return vectors.tolist() if hasattr(vectors, "tolist") else vectors


def _client():
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )


def build_index(
    chunks: list[Chunk],
    corpus: str | None = None,
    variant: str = "default",
) -> int:
    """
    Embed every chunk and store it.

    `variant` lets you keep more than one index of the same corpus at the same
    time. In unit 2, when you compare two chunking strategies, index the second
    one as variant="v2" and you can query both instead of deleting the first
    and starting over.
    """
    name = config.collection_name(corpus, variant)
    client = _client()

    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(
        name=name,
        # ⚠️ Do not remove. Chroma defaults to squared L2, and every distance
        # number in this course assumes cosine.
        metadata={"hnsw:space": "cosine", "embedding_model": config.EMBEDDING_MODEL},
    )

    batch = 256
    for start in range(0, len(chunks), batch):
        window = chunks[start : start + batch]
        collection.add(
            ids=[f"{c.source}#{c.index}" for c in window],
            documents=[c.text for c in window],
            embeddings=embed([c.text for c in window]),
            metadatas=[
                {
                    "source": c.source,
                    "index": c.index,
                    "produced_by": c.produced_by,
                    "category": c.category,
                }
                for c in window
            ],
        )

    return len(chunks)


def search(
    question: str,
    top_k: int | None = None,
    corpus: str | None = None,
    variant: str = "default",
    category: str | None = None,
    source: str | None = None,
) -> list[Result]:
    """
    Retrieve the chunks closest in meaning to a question.

    Returns them nearest-first, each with its distance. With
    config.RETRIEVAL = "hybrid" the order is the BM25 + cosine fused order
    instead, and each distance is still the chunk's cosine distance.

    `category` (e.g. "housing") and `source` (an exact filename) narrow the
    search to chunks with that metadata. Filtering happens inside Chroma, so
    top_k still means "the k nearest among the chunks that match".
    """
    top_k = top_k or config.TOP_K
    name = config.collection_name(corpus, variant)

    try:
        collection = _client().get_collection(name)
    except Exception as exc:
        raise RuntimeError(
            f"No index called '{name}'. Run `python app.py index` first."
        ) from exc

    built_with = (collection.metadata or {}).get("embedding_model")
    if built_with and built_with != config.EMBEDDING_MODEL:
        raise RuntimeError(
            f"Index '{name}' was built with {built_with!r} but "
            f"EMBEDDING_MODEL is {config.EMBEDDING_MODEL!r}. Distances between "
            f"two different models mean nothing. Set AI201_EMBEDDING_MODEL="
            f"{built_with} or search a different --variant."
        )

    filters = []
    if category:
        filters.append({"category": category})
    if source:
        filters.append({"source": source})
    where = None
    if len(filters) == 1:
        where = filters[0]
    elif filters:
        where = {"$and": filters}

    if where is not None:
        matching = len(collection.get(where=where, include=[])["ids"])
        if matching == 0:
            return []
    else:
        matching = collection.count()

    hybrid = config.RETRIEVAL == "hybrid"

    raw = collection.query(
        query_embeddings=embed([question]),
        # Hybrid fuses two rankings of every candidate, so it needs them all.
        # campus_life is 88 chunks; this is cheap.
        n_results=matching if hybrid else min(top_k, matching),
        where=where,
    )

    if hybrid:
        raw = _fuse_with_bm25(question, raw, top_k)

    results: list[Result] = []
    for text, meta, distance in zip(
        raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
    ):
        results.append(
            Result(
                text=text,
                source=str(meta.get("source", "unknown")),
                label=f"{meta.get('source', 'unknown')}#{meta.get('index', 0)}",
                distance=float(distance),
                produced_by=str(meta.get("produced_by", "unknown")),
            )
        )
    return results


def _tokens(text: str) -> list[str]:
    """Lowercase words and numbers, so "CS 210" becomes ["cs", "210"]."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _fuse_with_bm25(question: str, raw: dict, top_k: int) -> dict:
    """
    Re-rank Chroma's candidates by reciprocal rank fusion of two orderings:
    cosine distance (already sorted) and BM25 keyword score.

    Each chunk scores 1/(RRF_K + rank) from each list; the top_k by total
    score come back. Distances are left as Chroma's cosine distances, so the
    relevance gate still compares like with like.
    """
    from rank_bm25 import BM25Okapi

    docs = raw["documents"][0]
    bm25 = BM25Okapi([_tokens(d) for d in docs])
    keyword = bm25.get_scores(_tokens(question))
    by_keyword = sorted(range(len(docs)), key=lambda i: -keyword[i])

    # Chroma returned the candidates in cosine order, so index i is rank i + 1.
    fused = [1 / (config.RRF_K + i + 1) for i in range(len(docs))]
    for rank, i in enumerate(by_keyword, start=1):
        fused[i] += 1 / (config.RRF_K + rank)

    keep = sorted(range(len(docs)), key=lambda i: -fused[i])[:top_k]
    # Unit 2 stretch: never let fusion drop the closest cosine chunk. When a
    # question shares no keywords with its answer ("Can I bring a car?" vs the
    # parking post), BM25 is noise and would otherwise push it out — and then
    # the gate judges a worse best distance than the corpus really has.
    if 0 not in keep:
        keep[-1] = 0
    return {
        field: [[raw[field][0][i] for i in keep]]
        for field in ("documents", "metadatas", "distances")
    }


def index_exists(corpus: str | None = None, variant: str = "default") -> bool:
    """Is there an index here to search, without searching it?

    `serve.py`'s health check asks this. It deliberately does not embed
    anything: loading the embedding model takes 80 MB and a few seconds, and a
    health check that heavy is a health check nobody can afford to call.
    """
    try:
        collection = _client().get_collection(config.collection_name(corpus, variant))
        return collection.count() > 0
    except Exception:
        return False


def reset():
    """Delete every index. Occasionally the fastest way out of a mess."""
    if config.CHROMA_DIR.exists():
        shutil.rmtree(config.CHROMA_DIR)
