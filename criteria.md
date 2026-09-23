# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**How to check:** for each question in `questions.py`, run
`python app.py retrieve "<question>"` and see whether the file named in the
comment above that question appears among the five results.

**Why this target:**
Three of my five questions point at a file that has near-identical siblings.
Fenwick Court's laundry post is one of seven laundry posts that share almost
every word except the hall name. With 88 chunks and top-k 5, one of those
siblings could push the right file down to sixth. I'd call it a failure if
more than one question missed, but not if exactly one did.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**How to check:** every answer printed by `python app.py ask` (or written to
the run log by `run_eval.py`) contains at least one `.txt` filename from
`corpora/campus_life/documents/`.

**Why this target:**
All five and not four because the pipeline makes it easy. Every excerpt in the
prompt is labelled `[from <filename>]`, and `GROUNDING_INSTRUCTION` in
`generate.py` tells the model to name the file. Each of my five questions is
answered by a single short post, so there's always one obvious file to cite.
The only way to miss is the model ignoring an explicit instruction, which is
exactly the kind of failure I want to see.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**How to check:** `python run_eval.py` puts the five `OUT_OF_SCOPE` questions
through the gate and records, for each one, whether it was refused. Count the
refusals.

**Why this target:**
Four of the five (Mongolia, diesel engines, the World Cup, Rust) have nothing
near them in a corpus about one campus. The ibuprofen question is the risky
one. `health_center.txt` talks about walk-in hours and urgent visits, so that
question could land close enough to pass the gate. I'd rather allow for that
one near-miss than set the cutoff so tight that it refuses real campus
questions.

---

## 4. Every chunk keeps its title and is never a fragment

Every chunk printed by `python app.py chunks` begins with the first line (the
title) of the document it came from, and `python app.py index` reports no
chunk shorter than 150 characters.

**Why this target:**
Every `campus_life` document is a short post (178–549 characters after
cleaning): a title line like "PHYS 130 Mechanics — assessment" followed by 2–5
short paragraphs. The title is often the only place the subject gets named. A
line like "The lab practical is worth 20% and almost nobody prepares for it"
doesn't say which course it's about once it's cut away from that title. The
shortest real post is 178 characters, so anything under 150 can only be a
fragment left over from a bad split. It's "every chunk" and not "most" because
the model can't recover a subject that isn't in the chunk.

---

## 5. The cited source is the right one, not a sibling

For at least 4 of my 5 test questions, the answer names the file listed in the
comment above that question in `questions.py`. Naming only a sibling file from
the same course or hall does not count (for example, citing
`course_cs_210_workload.txt` when the answer is in `course_cs_210_exams.txt`).

**Why this target:**
The corpus is mostly near-identical templates: 9 courses × 3 files
(overview / exams / workload) and 7 residence halls × 3 files (overview /
laundry / noise). That's 48 of the 88 documents, and siblings share most of
their vocabulary, so their embeddings will sit close together. Criterion 2
only checks that a source is present. This one checks that it's correct,
which is where I expect this corpus to go wrong. 4 of 5 rather than 5 of 5
because my first two questions hit the CS 210 exams and workload files one
after the other. Both files will come back for both questions, and I expect
the model might cite the wrong one of the pair once. Two wrong citations
would mean the pipeline can't tell siblings apart.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
