"""
Ask my test-question templates about EVERY course, hall and dining hall.

My five test questions each name one entity (CS 210, Fenwick Court, Kestrel
Commons). This asks the same question shape for all of them, so I can see
whether retrieval tells siblings apart in general or only for the entities I
happened to pick. Retrieval only: no model calls.

    python tools/sibling_probe.py                  # writes results/sibling_probe_semantic.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
from store import search  # noqa: E402

COURSES = {
    "biol_160": "BIOL 160", "cs_210": "CS 210", "cs_340": "CS 340",
    "econ_101": "ECON 101", "engl_205": "ENGL 205", "hist_118": "HIST 118",
    "math_220": "MATH 220", "phys_130": "PHYS 130", "stat_150": "STAT 150",
}
HALLS = {
    "aldridge_hall": "Aldridge Hall", "calder_annexe": "Calder Annexe",
    "fenwick_court": "Fenwick Court", "innisfree_hall": "Innisfree Hall",
    "morrow_house": "Morrow House", "old_brewhouse": "Old Brewhouse",
    "tamsin_court": "Tamsin Court",
}
DINING = {
    "halden_hall": "Halden Hall", "kestrel_commons": "Kestrel Commons",
    "north_kitchen": "North Kitchen", "pellew_dining_hall": "Pellew Dining Hall",
    "the_atrium": "The Atrium", "the_ridgeway_cafe": "The Ridgeway Cafe",
    "verrill_street_grill": "Verrill Street Grill",
}


def probes():
    """(family, question, accepted files). Accepted = files that contain the answer."""
    for key, code in COURSES.items():
        yield "exams", f"Is the {code} final exam curved?", {f"course_{key}_exams.txt"}
        yield "workload", f"How many hours a week does {code} take outside class?", {f"course_{key}_workload.txt"}
    for key, name in HALLS.items():
        yield "laundry", f"When is the best time to do laundry in {name}?", {f"housing_{key}_laundry.txt"}
    for key, name in DINING.items():
        # The followup post repeats the wait figure, so either file answers it.
        yield "dining", f"How long is the lunch wait at {name}?", {f"dining_{key}.txt", f"dining_{key}_followup.txt"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="semantic", help="label for the output file")
    args = parser.parse_args()

    rows = []
    for family, question, accepted in probes():
        results = search(question)
        ranked = [r.source for r in results]
        hit_rank = next((i + 1 for i, s in enumerate(ranked) if s in accepted), None)
        rows.append({
            "family": family, "question": question, "accepted": sorted(accepted),
            "top5": [[r.source, round(r.distance, 4)] for r in results],
            "rank": hit_rank,
        })

    families = sorted({r["family"] for r in rows})
    print(f"mode: {args.mode}   top-k {config.TOP_K}")
    print(f"{'family':<10}{'n':>4}{'rank 1':>9}{'in top 5':>10}")
    for fam in families + ["ALL"]:
        sub = [r for r in rows if fam == "ALL" or r["family"] == fam]
        r1 = sum(r["rank"] == 1 for r in sub)
        t5 = sum(r["rank"] is not None for r in sub)
        print(f"{fam:<10}{len(sub):>4}{r1:>6}/{len(sub):<3}{t5:>6}/{len(sub):<3}")

    misses = [r for r in rows if r["rank"] != 1]
    if misses:
        print("\nNot at rank 1:")
        for r in misses:
            print(f"  rank {r['rank'] or '-'}  {r['question']}  -> top: {r['top5'][0][0]} ({r['top5'][0][1]})")

    out = config.RESULTS_DIR / f"sibling_probe_{args.mode}.json"
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nWrote {out.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
