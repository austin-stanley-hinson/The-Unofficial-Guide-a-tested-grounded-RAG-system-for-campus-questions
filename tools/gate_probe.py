"""
Put unit 1's borderline campus questions and the OUT_OF_SCOPE ones through
retrieval and the relevance gate. Retrieval only: no model calls.

Criterion 3 only checks that the gate refuses what it should. This also
checks the reverse: covered campus questions it should let through.

    python tools/gate_probe.py --mode hybrid    # writes results/gate_probe_hybrid.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
import gate  # noqa: E402
import questions as qs  # noqa: E402
from store import search  # noqa: E402

# From the unit 1 README's Milestone 4 probes: (question, does the corpus cover it?)
BORDERLINE = [
    ("Which dorm is quietest for studying?", True),
    ("How do I get a parking permit?", True),
    ("Is there a campus gym?", False),
    ("What's the best pizza place in town?", False),
    ("Is there a swimming pool on campus?", False),
    ("Where can I print documents?", True),
    ("Can I bring a car?", True),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=config.RETRIEVAL, help="label for the output file")
    args = parser.parse_args()

    rows = []
    for question, covered in BORDERLINE + [(q, False) for q in qs.OUT_OF_SCOPE]:
        results = search(question)
        decision = gate.check(results)
        rows.append({
            "question": question, "covered": covered,
            "best_distance": round(decision.best_distance, 4),
            "passed": decision.passed,
            "top5": [[r.source, round(r.distance, 4)] for r in results],
        })

    print(f"mode: {args.mode}   cutoff {config.THRESHOLD}")
    for r in rows:
        tag = "covered " if r["covered"] else "uncovered"
        print(f"  {tag}  {r['best_distance']:.4f}  {'pass  ' if r['passed'] else 'REFUSE'}  {r['question']}")
    covered = [r for r in rows if r["covered"]]
    oos = rows[len(BORDERLINE):]
    print(f"covered questions let through: {sum(r['passed'] for r in covered)}/{len(covered)}")
    print(f"out-of-scope refused:          {sum(not r['passed'] for r in oos)}/{len(oos)}")

    out = config.RESULTS_DIR / f"gate_probe_{args.mode}.json"
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Wrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
