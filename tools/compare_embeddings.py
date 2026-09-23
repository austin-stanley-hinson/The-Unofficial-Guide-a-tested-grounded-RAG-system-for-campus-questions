"""
Stretch: dump top-5 retrieval for the same queries under one embedding model.

    python tools/compare_embeddings.py default results/embedding_minilm.json
    AI201_EMBEDDING_MODEL=all-mpnet-base-v2 \
        python tools/compare_embeddings.py mpnet results/embedding_mpnet.json

Build the matching index first (`python app.py --variant mpnet index`, with
the same AI201_EMBEDDING_MODEL). store.search refuses to mix models.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
import questions  # noqa: E402
import store  # noqa: E402

# Borderline campus questions probed in Milestone 4 (see README).
PROBES = [
    "Which dorm is quietest for studying?",
    "How do I get a parking permit?",
    "Is there a campus gym?",
    "What's the best pizza place in town?",
    "Is there a swimming pool on campus?",
    "Where can I print documents?",
    "Can I bring a car?",
]


def main():
    variant, out_path = sys.argv[1], sys.argv[2]
    queries = [q["question"] for q in questions.QUESTIONS] + questions.OUT_OF_SCOPE + PROBES
    out = {"embedding_model": config.EMBEDDING_MODEL, "variant": variant, "results": {}}
    for query in queries:
        results = store.search(query, variant=variant)
        out["results"][query] = [(r.source, round(r.distance, 4)) for r in results]
    Path(out_path).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {len(queries)} queries to {out_path}")


if __name__ == "__main__":
    main()
