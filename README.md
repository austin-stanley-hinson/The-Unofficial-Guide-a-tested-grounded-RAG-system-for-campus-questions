# The Unofficial Guide

Austin Stanley Hinson — corpus: `campus_life` (88 short student posts about dining, housing, courses and campus admin).

---

# Unit 1

## What This Does

The Unofficial Guide answers plain-English questions about student life at
one university, using the `campus_life` corpus: 88 short posts written by
students about dining halls, residence halls, specific courses, and the
administrative rules nobody explains properly. It answers questions like
"Is the CS 210 final curved?", "When is the laundry room empty in Fenwick
Court?", "How long is the lunch line at Kestrel Commons?" or "Do dining
dollars roll over?". Every answer names the post it came from. Questions the
posts don't cover ("Who won the 1994 World Cup?") get "I don't have enough
information about that" instead of a guess. Run it with
`python app.py ask "your question"`.

## Chunking Strategy

**Chunk size:** 600 characters maximum. In practice that means one post = one chunk.
**Overlap:** 0 characters. Instead, the post's title line is repeated at the top of every piece if a post ever has to split.

What I saw when I read the documents in Milestone 1: every `campus_life` post
is a title line ("PHYS 130 Mechanics — assessment", "Laundry in Fenwick
Court") followed by 2–5 short paragraphs. The whole post runs 178–549
characters (`python app.py index` reports shortest 178, longest 549). Two
things follow from that:

1. **The title is often the only place the subject is named.** The PHYS 130
   post's last line is "The lab practical is worth 20% and almost nobody
   prepares for it." On its own, that line doesn't say which course. Any
   split that separates a paragraph from its title throws the subject away.
   So `split_documents` packs whole paragraphs under the title, and if a
   post ever needs splitting, every piece gets the title again. That repeated
   title is my overlap. A 120-character window of borrowed text would carry
   half a sentence; the title carries the one thing the piece can't do
   without.
2. **Posts are already one thought each.** Near-identical sibling files
   (`course_cs_210_exams.txt` / `course_cs_210_workload.txt`,
   `housing_fenwick_court_laundry.txt` / `housing_fenwick_court_noise.txt`)
   mean the corpus's authors already split topics at the file level. Cutting
   further would only produce fragments.

Why 600 and not something smaller: I tried `CHUNK_SIZE = 250` to see what
paragraph-level chunks would look like. It made 162 chunks, and the shortest
was 69 characters, a title plus one clause. That breaks criterion 4 (no
chunk under 150). 600 sits just above the longest post (549), so nothing
splits. If a longer post were added, it would split on a paragraph break
rather than mid-sentence.

Honest note: on this corpus the starter's `fallback_split` at 800 characters
*also* produced 88 whole-post chunks, because nothing reaches 800. The
difference is what happens at the edges: `fallback_split` cuts mid-word and
drops the title from every piece after the first. `split_documents` never
does either.

One thing I noticed while reading the chunks: sibling files aren't perfectly
separated. `housing_innisfree_hall.txt` (the overview) also mentions the
laundry price. That could matter for criterion 5, because a laundry question
could fairly be answered from the overview file.

## Sample Chunks

Printed with `python app.py chunks -n 5` and copied across.

**Chunk 1** — source: `admin_add_drop_deadline.txt` (chunk #0) — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt` (chunk #0) — produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt` (chunk #0) — produced by: `chunker.py::split_documents`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt` (chunk #0) — produced by: `chunker.py::split_documents`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall.txt` (chunk #0) — produced by: `chunker.py::split_documents`

```
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

**Question:** When is the best time to do laundry in Fenwick Court?

**Answer:**

```
$ python app.py ask "When is the best time to do laundry in Fenwick Court?"
  (best distance 0.295, cutoff 0.7)

The best time to do laundry in Fenwick Court is Tuesday or Wednesday morning.
Source: housing_fenwick_court_laundry.txt

Sources retrieved: housing_aldridge_hall_laundry.txt, housing_fenwick_court_laundry.txt, housing_old_brewhouse_laundry.txt, housing_tamsin_court_laundry.txt, transit_walking.txt
```

Four laundry posts from four different halls came back. The answer cites only
the Fenwick Court one, which is what criterion 5 is testing.

**My relevance cutoff:** `THRESHOLD = 0.7` in `config.py`.

I ran each question through `python app.py retrieve` and wrote down the best
distance:

| Question | In corpus? | Best distance |
|---|---|---|
| Is the CS 210 final exam curved? | Yes | 0.3596 |
| How many hours a week does CS 210 take outside class? | Yes | 0.3003 |
| When is the best time to do laundry in Fenwick Court? | Yes | 0.2951 |
| How long is the lunch wait at Kestrel Commons? | Yes | 0.1832 |
| Do dining dollars roll over from spring to fall? | Yes | 0.2192 |
| What is the capital of Mongolia? | No | 0.8246 |
| How do I change the oil in a diesel engine? | No | 0.9340 |
| Who won the 1994 World Cup? | No | 0.8859 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.8442 |
| How do I write a for loop in Rust? | No | 0.8960 |

The two groups are far apart: in-corpus 0.18–0.36, out-of-corpus 0.82–0.93,
with nothing between 0.36 and 0.82. The ibuprofen question I was worried
about in criterion 3 didn't land near `health_center.txt` at all. Its closest
chunk was `money_textbooks.txt` at 0.84.

The midpoint of that gap is about 0.59, so the starter's 0.6 would have
worked for these ten. I didn't stop there, because my five test questions are
unusually specific: each one names a course, hall or dining hall. I probed a
few shorter, vaguer campus questions:

| Question | Covered? | Best distance |
|---|---|---|
| Which dorm is quietest for studying? | Yes (noise posts) | 0.4797 |
| How do I get a parking permit? | Yes | 0.5339 |
| Is there a campus gym? | No | 0.5748 |
| What's the best pizza place in town? | No | 0.5802 |
| Is there a swimming pool on campus? | No | 0.6254 |
| Where can I print documents? | Partly (printing quota) | 0.6802 |
| Can I bring a car? | Yes (parking permits) | 0.6998 |

Real campus questions reach 0.70, and uncovered campus-flavoured questions
start at 0.57. The two groups overlap, so no cutoff separates them cleanly.
I set 0.7: it lets real campus questions through, and it still sits 0.12
below the closest truly out-of-corpus question (0.82). What I get wrong at
0.7: questions like the pizza one (0.58) pass the gate and reach the model.
For those I'm relying on the second layer. I checked, and the model said "I
don't have enough information" for the pizza question. "Can I bring a car?"
at 0.6998 only just passes, so a slightly vaguer wording would be refused.

**Grounding change:** before tightening it, the model's refusal to "Where
can I print documents?" still listed five source files. I added two rules to
`GROUNDING_INSTRUCTION` in `generate.py`: name only the files that actually
contain the facts used (not every file provided), and name no source when
declining. After the change the same question returns a plain "I do not have
enough information" with no citation.

## How I Used AI

I used Claude Code throughout. Two moments where what came back wasn't what I kept:

**1. Criterion 4.** I asked Claude to help me write criterion 4 from what
the posts looked like. Its first draft was "In 5 of 5 sampled chunks, I can
tell which course, residence hall, or topic the chunk is about from the chunk
alone." When I checked it against the rubric's "testable by a stranger" line,
"I can tell" turned out to be a judgment only I could make. We rewrote it as
two checks anyone can run: every chunk starts with its document's title
line, and `app.py index` reports no chunk under 150 characters. The 150
comes from the corpus: the shortest real post is 178 characters.

**2. The grounding instruction.** I asked Claude to test the 0.7 cutoff on
borderline questions. "Where can I print documents?" (0.68) passed the gate,
and the model correctly said it didn't know. But it still listed five
"sources" under that non-answer: `admin_printing_quota.txt`,
`money_textbooks.txt` and three others. The starter's grounding instruction
only says to name a file, not to name the *right* file. With 48 sibling
files in this corpus, that's exactly the criterion 5 failure I wrote down. I
added two rules to `GROUNDING_INSTRUCTION`: cite only files whose facts you
used, and cite nothing when declining. Then I re-ran the same question and
the citation list was gone.

**Unit 2.** Claude Code ran the evals and helped read the results. Three
moments mattered:

- **The first before-run was garbage, and it looked like a finding.** Every
  question came back refused at 0.86–0.95. Instead of writing that up as
  "the gate refuses everything", Claude compared the stored vectors with
  fresh embeddings (cosine ≈ 0). The cause was `tools/smoke_test.py` having
  overwritten the index with fake embeddings. Recording that run would have
  meant diagnosing a bug my system doesn't have.
- **Finding the pattern.** With everything MET, I had Claude run the same
  question shapes over every course, hall and dining hall. The 7 misses all
  being course questions, plus the 0.27 distance between "CS 210" and
  "CS 340", is what turned seven failures into one diagnosis.
- **Arguing against my own result.** Criterion 5's verdict was checked by
  arguing the opposite (the extra sibling citation), and the hybrid change
  was checked against unit 1's borderline questions, not just my five.
  That second check is what found the regression. My criteria alone would
  have reported the change as harmless.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

## Stretch Features

Declared here before building any of them. Results for each are filled in
below as it's finished.

1. **Metadata filtering.** Every chunk gets a `category` from its filename
   prefix (`admin`, `course`, `dining`, `housing`, …) alongside its `source`.
   `retrieve` and `ask` get `--category` and `--source` flags that narrow the
   search to those chunks. The point is the sibling problem: a laundry
   question restricted to one hall's files can't pull in another hall's.
2. **Conversational memory.** A `python app.py chat` mode where a follow-up
   ("what about before 11:45?") is rewritten into a standalone question using
   the previous turn before retrieval runs, and the previous exchange is
   passed to the model with the new excerpts.
3. **A second embedding model.** Index the same chunks with
   `all-mpnet-base-v2` (768 dimensions, via `sentence-transformers`) as a
   separate variant, and re-run the same ten cutoff questions plus the
   borderline probes against both. I'll record which results and distances
   moved, and whether my 0.7 cutoff still holds.

### Stretch 1 result: metadata filtering

**What I built:** every chunk now stores a `category` (its filename prefix,
from `Chunk.category` in `chunker.py`) next to `source` in Chroma.
`store.py::search` takes `category=` and `source=` and passes them to Chroma
as a `where` filter, so filtering happens *before* the top-k is taken, not
after. `python app.py retrieve` and `python app.py ask` both accept
`--category NAME` and `--source FILE`.

**Same query, with and without the filter:**

```
$ python app.py ask "Where is a quiet place to study late at night?"
  (best distance 0.481, cutoff 0.7)
If you need quiet to work, most people go to the library, which is open until 2am during term.
Sources: housing_fenwick_court_noise.txt, study_library_hours.txt, housing_morrow_house_noise.txt, housing_innisfree_hall_noise.txt, housing_aldridge_hall_noise.txt
Sources retrieved: housing_aldridge_hall_noise.txt, housing_fenwick_court_noise.txt, housing_innisfree_hall_noise.txt, housing_morrow_house_noise.txt, study_library_hours.txt

$ python app.py ask "Where is a quiet place to study late at night?" --category study
  (best distance 0.485, cutoff 0.7)
The library is open until 2am during term (and until 10pm during reading week). The third floor is silent and enforced, while the second floor is quiet in theory.
Source: study_library_hours.txt
Sources retrieved: study_group_rooms.txt, study_library_hours.txt
```

**What changed:** without the filter, 4 of the 5 retrieved chunks were
residence-hall noise posts (0.481–0.495), because "quiet" and "late at
night" are exactly their vocabulary. They all mention the library in
passing, so the answer was a generic "go to the library" citing five files.
With `--category study`, only the two `study_*` posts are searched (that's
all there are), and the answer gets specific: which floor is silent, and
reading-week hours. It cites one file. The best distance barely moved
(0.481 → 0.485). The filter didn't find a closer chunk; it removed the
distractors.

**Second example, the sibling problem:** "When is the best time to do
laundry in Fenwick Court?" unfiltered pulls in `transit_walking.txt` at #3
(0.484). With `--category housing` that's replaced by
`housing_fenwick_court.txt` (0.510), the Fenwick overview post. With
`--source housing_fenwick_court_laundry.txt` only the one right chunk comes
back (0.2951).

**Something the filter can break:** filtering interacts with the relevance
gate. "How much does it cost?" unfiltered has a best distance of 0.582
(`housing_calder_annexe.txt`). With `--category dining` the best is 0.747
(`dining_north_kitchen.txt`), which is over my 0.7 cutoff, so the gate
refuses. A filter can push a question from "answered" to "refused" when the
nearest chunk overall is outside the category.

### Stretch 2 result: conversational memory

**What I built:** `python app.py chat`. Every turn after the first goes
through `generate.py::rewrite_followup`, which uses one model call to turn
the follow-up into a standalone question using the last
`CHAT_MEMORY_TURNS = 2` turns. Retrieval and the relevance gate then run on
the rewritten question, not the raw one. That was the key decision:
retrieval embeds only the question, so "does it close…" with no subject
would search for nothing in particular. The earlier exchange also goes into
the answer prompt (`build_prompt(..., history=...)`), marked "for context
only; facts must still come from the documents".

**Two-turn exchange where the second answer depends on the first:**

```
$ python app.py chat
> How long is the lunch wait at Kestrel Commons?
  (best distance 0.183, cutoff 0.7)

The lunch wait at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00, and under 5 minutes before 11:45.
Sources: dining_kestrel_commons.txt, dining_kestrel_commons_followup.txt

> What time does it close on weekends?
  (searched as: What time does Kestrel Commons close on weekends?)
  (best distance 0.407, cutoff 0.7)

Kestrel Commons is open until 9:00pm on weekdays and 8:00pm on weekends. Halden Hall closes at 7:00pm on weekdays and is closed Sundays.
Sources: dining_kestrel_commons.txt, dining_halden_hall.txt

> Is the salad bar any good there?
  (searched as: Is the salad bar at Kestrel Commons any good?)
  (best distance 0.357, cutoff 0.7)

The salad bar at Kestrel Commons wilts after 1:30.
Sources: dining_kestrel_commons.txt, dining_kestrel_commons_followup.txt
```

"It" in turn 2 and "there" in turn 3 only mean Kestrel Commons because of
turn 1. Without memory, the same second question gets nothing useful:

```
$ python app.py ask "What time does it close on weekends?"
  (best distance 0.488, cutoff 0.7)
I do not have enough information to answer what time it closes on weekends.
Sources retrieved: dining_halden_hall.txt, dining_halden_hall_followup.txt, dining_north_kitchen_followup.txt, housing_calder_annexe_noise.txt, transit_shuttle.txt
```

Without the subject, retrieval drifted to Halden Hall and the shuttle, and
`dining_kestrel_commons.txt` didn't even make the top 5. The rewrite brought
the best distance from 0.488 down to 0.407 and put the right file first.

**What's still wrong:** the turn 2 answer volunteers Halden Hall's hours,
which nobody asked about. Halden was retrieved alongside Kestrel and the
model used it. The cost is one extra model call per follow-up (4 calls for
the 3-turn exchange above instead of 3).

### Stretch 3 result: a second embedding model

**What I built:** `EMBEDDING_MODEL` in `config.py` can now be overridden with
`AI201_EMBEDDING_MODEL`. I indexed the same 88 chunks with
`all-mpnet-base-v2` (768 dimensions, loaded through `sentence-transformers`)
as a separate variant, so the default MiniLM index stayed untouched:

```
pip install 'sentence-transformers>=3.4,<3.5'
AI201_EMBEDDING_MODEL=all-mpnet-base-v2 python app.py --variant mpnet index
AI201_EMBEDDING_MODEL=all-mpnet-base-v2 python app.py --variant mpnet retrieve "..."
```

Each index records which model built it, and `store.py::search` refuses to
search it with a different one. Comparing distances across two models is
meaningless, and that's an easy mistake to make without noticing.
`tools/compare_embeddings.py` ran all 17 queries (my 5, the 5 `OUT_OF_SCOPE`,
and the 7 borderline probes) against both indexes. The raw top-5 lists are
in `results/embedding_minilm.json` and `results/embedding_mpnet.json`.

**Best distance and top result, same queries, both models:**

| Question | MiniLM (default) | mpnet | Top result changed? |
|---|---|---|---|
| Is the CS 210 final exam curved? | 0.3596 `course_cs_210_exams` | 0.4431 `course_phys_130_exams` | **Worse:** right file drops to #3 (0.5557) |
| How many hours a week does CS 210 take outside class? | 0.3003 | 0.3683 | Same (`course_cs_210_workload`) |
| When is the best time to do laundry in Fenwick Court? | 0.2951 | 0.2568 | Same; `transit_walking` at #3 replaced by another laundry post |
| How long is the lunch wait at Kestrel Commons? | 0.1832 `…_followup` | 0.1871 `dining_kestrel_commons` | Swapped the two Kestrel posts |
| Do dining dollars roll over from spring to fall? | 0.2192 | 0.2210 | Same |
| What is the capital of Mongolia? | 0.8246 | 0.8134 | Same |
| How do I change the oil in a diesel engine? | 0.9340 | 0.8163 | Now all 5 are laundry posts ("machines") |
| Who won the 1994 World Cup? | 0.8859 | 0.9135 | Same |
| Ibuprofen dosage for a headache? | 0.8442 | 0.8515 | Different, still unrelated |
| How do I write a for loop in Rust? | 0.8960 | **0.7916** | Now laundry posts and `course_cs_210_exams` |
| Which dorm is quietest for studying? | 0.4797 | 0.4272 | Better: top 3 are all noise posts |
| How do I get a parking permit? | 0.5339 | 0.4849 | Same (`admin_parking_permits`) |
| Can I bring a car? | 0.6998 | **0.7211** | Same file, but now over my 0.7 cutoff |

**What moved, and in which direction:**

- **In-corpus questions got further away, not closer.** 3 of my 5 test
  questions got worse (CS 210 exams +0.08, CS 210 workload +0.07, Kestrel
  +0.004). One improved (Fenwick laundry −0.04), and one was flat.
- **The course-code problem got worse.** mpnet ranks "Is the CS 210 final
  curved?" closest to PHYS 130's exam post. mpnet seems to weigh the meaning
  of "is the final curved" over the literal course code, and in this corpus
  the course code is the thing that matters. This is exactly the sibling
  failure criterion 5 is about, and mpnet makes it happen at rank 1.
- **Out-of-corpus questions got closer.** The Rust question fell from 0.896
  to 0.792, and the diesel one from 0.934 to 0.816. mpnet matches "machines"
  and "code" in a looser, more topical way. The gap between my two groups
  shrank from 0.36–0.82 to 0.44–0.79.
- **The cutoff would have to move.** At 0.7, mpnet refuses "Can I bring a
  car?" (0.7211), which MiniLM just answered. Under mpnet the cutoff would
  need to be about 0.75, which leaves only 0.04 of room below the Rust
  question (0.79).
- **Where mpnet was better:** vaguer, meaning-level questions. "Which dorm
  is quietest?" (0.48 → 0.43, all three top hits are noise posts) and "How
  do I get a parking permit?" (0.53 → 0.48).

**Decision:** I kept `all-MiniLM-L6-v2` as the default. This corpus's hard
part is telling near-identical siblings apart by a course code or hall name,
and the bigger model is worse at exactly that. It also needs PyTorch.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Every chunk keeps its title, none under 150 chars | 88 of 88 | 88/88 | 88/88 | 88/88 | MET |
| 5. Cited source is the right file, not a sibling | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Raw file: `results/run_2026-09-29_2220_before.md`, written by
`run_eval.py::main` (questions) and `run_eval.py::check_out_of_scope`
(criterion 3). There's no `scorer.py`, so I scored every answer by reading
it against the file named in `questions.py`.

Criteria 1, 3 and 4 don't depend on the model, so the same number goes in all
three columns. Retrieval, the gate and the chunker are deterministic. The
generated answers did vary between runs, which shows the cache really was off:
the Kestrel answer cited `dining_kestrel_commons_followup.txt` in runs 1 and 3
but not run 2, and the dining-dollars answer dropped "whatever is left in May
disappears" in run 3.

**Something I caught before this run counted.** My first attempt came back
with every in-corpus question at 0.86–0.95 and all five refused by the gate.
Last unit those questions scored 0.18–0.36. I compared the stored vectors
with fresh embeddings of the same chunk text and got a cosine similarity of
about 0. `tools/smoke_test.py` sets `AI201_FAKE_EMBEDDINGS=1` and rebuilds
`campus_life__default`, and I'd run it after my last unit 1 commit, so it had
overwritten the real index with fake vectors. I rebuilt with
`python app.py index` (no code changed), confirmed the CS 210 and Fenwick
distances matched unit 1 exactly (0.3596, 0.2951), deleted that invalid run
file and re-ran.

### Real output (run 1)

**Criterion 1.** `store.py::search`. The expected file is in the top 5 for
all five questions (from the run log's "Sources retrieved" lines):

```
Is the CS 210 final exam curved?            -> course_cs_210.txt, course_cs_210_exams.txt, course_cs_340_exams.txt, course_engl_205_exams.txt, course_hist_118.txt
How many hours a week does CS 210 take...?  -> course_cs_210_workload.txt, course_cs_340.txt, course_econ_101_workload.txt, course_stat_150.txt, course_stat_150_workload.txt
When is the best time to do laundry in FC?  -> housing_aldridge_hall_laundry.txt, housing_fenwick_court_laundry.txt, housing_old_brewhouse_laundry.txt, housing_tamsin_court_laundry.txt, transit_walking.txt
How long is the lunch wait at Kestrel...?   -> dining_halden_hall_followup.txt, dining_kestrel_commons.txt, dining_kestrel_commons_followup.txt, dining_pellew_dining_hall_followup.txt, dining_the_ridgeway_cafe_followup.txt
Do dining dollars roll over...?             -> admin_dining_dollars.txt, admin_meal_plan_changes.txt, dining_halden_hall.txt, dining_north_kitchen.txt, money_jobs.txt
```

**Criteria 2 and 5.** `generate.py::answer_from_chunks`. Each answer names
a file, and it's the expected one:

```
No, the CS 210 final exam is not curved.
Sources: `course_cs_210_exams.txt`, `course_cs_210.txt`

CS 210 takes 8 to 10 hours a week outside class.
Source: course_cs_210_workload.txt

The best time to do laundry in Fenwick Court is Tuesday or Wednesday morning.
Source: housing_fenwick_court_laundry.txt

The wait time at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00, and under 5 minutes before 11:45.
Source: dining_kestrel_commons.txt (and dining_kestrel_commons_followup.txt)

No, dining dollars do not roll over from the spring semester to the following autumn; whatever is left in May disappears.
Source: admin_dining_dollars.txt
```

**Criterion 3.** `run_eval.py::check_out_of_scope`, cutoff 0.7:

```
  refused  (best distance 0.825)  What is the capital of Mongolia?
  refused  (best distance 0.934)  How do I change the oil in a diesel engine?
  refused  (best distance 0.886)  Who won the 1994 World Cup?
  refused  (best distance 0.844)  What is the recommended dosage of ibuprofen for a headache?
  refused  (best distance 0.896)  How do I write a for loop in Rust?
  -> gate refused 5 of 5
```

**Criterion 4.** `chunker.py::split_documents`, from `python app.py index`
plus a check that every chunk starts with its document's first line:

```
  chunked  88 chunks, 317 characters on average (shortest 178, longest 549), produced by chunker.py::split_documents
88 chunks; missing title: 0 [] ; shortest: 178
```

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer (4 of 5) | MET | 5/5 in all three runs. Every expected file was in the top 5, and in fact at rank 1, except Kestrel, where `_followup` (which repeats the same "20 to 25 minutes") was #1 and the main post #2. |
| 2 | Every answer names a source (5 of 5) | MET | 15 of 15 answers contained at least one `.txt` filename. No run dropped the citation. |
| 3 | Gate stops out-of-corpus questions (4 of 5) | MET | 5/5 refused. The closest was Mongolia at 0.825, 0.125 over the cutoff. The ibuprofen question I worried about scored 0.844 and never got near `health_center.txt`. |
| 4 | Every chunk keeps its title, none under 150 chars | MET | 88/88 chunks start with their document's first line, and the shortest is 178. Deterministic, so it can't vary run to run. |
| 5 | Cited source is the right file, not a sibling (4 of 5) | MET | 15 of 15 answers named the expected file. The closest call is below. |

**Where I argued the other side.** Criterion 5: the CS 210 exams answer
cited `course_cs_210_exams.txt` *and* `course_cs_210.txt` (the overview) in
all three runs, and the overview is a sibling. My criterion says naming
*only* a sibling fails, and naming the expected file passes. The overview
also genuinely contains "Midterms are curved, the final is not", so it isn't
a wrong citation either. I kept MET. But I'll admit the criterion never said
what to do with an extra, correct sibling, and I only noticed that now.
The Kestrel answer citing `_followup` alongside the main post is the same
case.

No criterion is revised. All five could be measured as written, and none was
missed, so there's nothing to revise for the right reason.

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

**I missed nothing.** Honestly, that says more about my targets than about
the system. All five test questions name an entity the embedder happens to
tell apart, and "4 of 5 in the top 5" left room for a lot to go wrong
unnoticed. So I tested the same question shapes more widely to find where
the system actually breaks.

**Widening the test.** `tools/sibling_probe.py` asks my templates ("Is the
X final exam curved?", "How many hours a week does X take outside class?",
"When is the best time to do laundry in X?", "How long is the lunch wait at
X?") for every course, hall and dining hall: 32 questions, retrieval only,
no model calls. It counts a hit when the file that holds the answer comes
back at rank 1. Output: `results/sibling_probe_semantic.json`.

```
family       n   rank 1  in top 5
dining       7     7/7       7/7
exams        9     6/9       9/9
laundry      7     7/7       7/7
workload     9     5/9       8/9
ALL         32    25/32     31/32

Not at rank 1:
  rank 2  Is the CS 340 final exam curved?  -> top: course_cs_210_exams.txt (0.39)
  rank 4  How many hours a week does CS 340 take outside class?  -> top: course_cs_210_workload.txt (0.2996)
  rank 2  How many hours a week does ENGL 205 take outside class?  -> top: course_stat_150_workload.txt (0.3934)
  rank -  How many hours a week does HIST 118 take outside class?  -> top: course_stat_150_workload.txt (0.3839)
  rank 5  Is the MATH 220 final exam curved?  -> top: course_engl_205_exams.txt (0.4665)
  rank 3  How many hours a week does MATH 220 take outside class?  -> top: course_stat_150_workload.txt (0.3598)
  rank 2  Is the STAT 150 final exam curved?  -> top: course_engl_205_exams.txt (0.4287)
```

**The pattern: all 7 misses are course questions, and each one loses to a
different course's post of the same type.** Halls and dining halls are 14/14.
One problem, not seven.

**Stage: embedding, showing up at retrieval.** The mechanism:

- The sibling posts are one template with the course code and one figure
  swapped. `course_stat_150_workload.txt` and `course_hist_118_workload.txt`
  match word for word except "STAT 150 Applied Statistics" / "HIST 118 Modern
  World History" and "5 to 6 hours a week" / "about 120 pages a week".
- In a question, the course code is the only word that picks the right
  sibling, and MiniLM barely encodes it. Measured with `store.py::embed`:
  "CS 210" vs "CS 340" is 0.27 apart, while two hall names ("Fenwick Court"
  vs "Tamsin Court") are 0.58 apart. The question "How many hours a week does
  CS 340 take outside class?" sits 0.26 from the phrase "hours a week outside
  class" and 0.55 from "CS 340". The code is a small part of what the vector
  represents.
- So ranking is decided by which sibling shares the question's *template
  words*. STAT 150's post contains the literal "hours a week outside class",
  so it wins three workload questions it has nothing to do with. HIST 118's
  post says "pages a week", so it drops out of the top 5 entirely.
- Hall and dining names are ordinary words ("Fenwick", "Kestrel") that the
  embedder does encode, which is why those 14 all land at rank 1.

That's also why my own two CS 210 questions passed: CS 210's posts happen to
share the most wording with my question templates. The CS 210 workload
answer beat STAT 150 by just 0.056 (0.3003 vs 0.3563).

**What I'd tighten.** Criterion 1: from "in the top 5 for 4 of 5 of my
questions" to "at rank 1 for at least 30 of the 32 sibling-probe questions".
Today that's a MISS at 25/32. Criterion 5 would follow: a model reading a
top 5 where the wrong course is #1 is set up to cite it.

## The Improvement

**What I changed:** hybrid search. `store.py::search` now scores every
candidate chunk two ways: cosine distance (as before) and BM25 keyword score
(`rank-bm25`, over lowercase word/number tokens, so "CS 340" becomes `cs`,
`340`). `store.py::_fuse_with_bm25` merges the two rankings by reciprocal
rank fusion: each chunk gets `1/(60 + rank)` from each list, and the top 5
by total come back. Each result keeps its cosine distance, so the gate and
the 0.7 cutoff weren't touched. `RETRIEVAL = "hybrid"` in `config.py`;
`AI201_RETRIEVAL=semantic` reproduces unit 1 exactly (the sibling probe
gives the same 25/32 either way). `RRF_K = 60` is the standard constant, and
I didn't tune it.

**Why I picked it:** the diagnosis says course questions lose to another
course's identical template because the embedder barely encodes the course
code, and BM25 scores exactly that token.

### Run Log — After

Raw file: `results/run_2026-09-29_2226_after.md` (`run_eval.py::main`,
`run_eval.py::check_out_of_scope`).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Every chunk keeps its title, none under 150 chars | 88 of 88 | 88/88 | 88/88 | 88/88 | MET |
| 5. Cited source is the right file, not a sibling | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Criterion 4 is unchanged by construction: chunking wasn't touched and the
index wasn't rebuilt.

**Real output (run 1), where hybrid changed something:**

```
Is the CS 210 final exam curved?
  before: course_cs_210_exams, course_engl_205_exams, course_cs_210, course_cs_340_exams, course_hist_118
  after:  course_cs_210_exams, course_cs_210, course_cs_340_exams, course_cs_340, course_hist_118_exams
  No, the CS 210 final exam is not curved.
  Sources: course_cs_210_exams.txt, course_cs_210.txt

How many hours a week does CS 210 take outside class?
  before: course_cs_210_workload, course_stat_150_workload, course_cs_340, course_econ_101_workload, course_stat_150
  after:  course_cs_210_workload, course_stat_150_workload, course_stat_150, course_econ_101_workload, course_cs_210
  CS 210 takes 8 to 10 hours a week outside of class.
  Source: course_cs_210.txt and course_cs_210_workload.txt

  refused  (best distance 0.869)  What is the capital of Mongolia?          (was 0.825)
  refused  (best distance 0.860)  What is the recommended dosage of ibuprofen for a headache?   (was 0.844)
  refused  (best distance 0.900)  How do I write a for loop in Rust?        (was 0.896)
  -> gate refused 5 of 5
```

(The before/after orders are from `store.py::search` in each mode. The
answers are verbatim from the after run log.)

**Did it help?** For the problem it targeted, yes. On my five criteria, it
can't show: they were 5/5 before and 5/5 after, which is the "targets set
low" point from the diagnosis again. The measurement that could move was the
sibling probe (`results/sibling_probe_hybrid.json`):

```
                  semantic   hybrid
exams      (9)      6/9       9/9
workload   (9)      5/9       6/9
laundry    (7)      7/7       7/7
dining     (7)      7/7       7/7
ALL rank 1 (32)    25/32     29/32
ALL top 5  (32)    31/32     31/32
```

Exam questions went to 9/9. That's the course-code failure fixed where the
code is the only difference. Workload improved less. CS 340 is still rank
4, because CS 210's post shares the question's literal "outside class" and
BM25 rewards that as much as `340`. HIST 118 is still missing from the top 5,
because its post never says "hours", so neither method connects it. 29/32
still misses the 30/32 I proposed in the diagnosis.

**And it made something worse, which my criteria didn't catch.** I re-ran
unit 1's borderline campus questions through the gate:

```
                                        semantic          hybrid
Where can I print documents?            0.6802 pass   ->  0.7444 REFUSE
Can I bring a car?                      0.6998 pass   ->  0.8286 REFUSE
Is there a swimming pool on campus?     0.6254 pass   ->  0.6928 pass
```

Two questions the corpus does answer are now refused. The mechanism: BM25
has no stemming ("print" ≠ "printing"), and "car" and "bring" appear nowhere
in `admin_parking_permits.txt`. The right post scores 0 on keywords, so it
ranks near the bottom of the BM25 list. RRF weights that no-signal list the
same as the semantic one, so chunks that rank middling on both beat the
semantic #1 and push it out of the top 5. The gate then only sees worse
chunks. For short questions with no distinctive keyword, hybrid actively
hurts. The same effect raised the out-of-corpus distances (Mongolia 0.825 →
0.869): harmless there, but it's the same bug.

I left it this way for the measured run, because the unit allows one change
and a patch on top would make before/after impossible to read. The fix is in
What's Still Broken.

## Unit 2 Stretch: A Second Improvement

*This is the Unit 2 stretch. It's separate from the three Unit 1 stretch
features (metadata filtering, conversational memory, second embedding model)
listed under Unit 1 above.*

**Declared before building.** The change: hybrid fusion will always keep the
semantic #1 chunk in the results. If reciprocal rank fusion would drop it,
it replaces the lowest-ranked fused chunk. Because that chunk has the
smallest cosine distance of all candidates, the gate then judges the same
best distance it did in unit 1, and the model always sees the closest chunk.

**The failure it targets:** the hybrid regression above. "Where can I print
documents?" and "Can I bring a car?" were refused because a zero-signal BM25
list pushed the semantic #1 out of the top 5.

**How I'll measure it:** a third run log (`run_eval.py --label stretch`) in
the same five-criteria table, the gate on unit 1's 7 borderline questions
plus the 5 out-of-scope ones (`tools/gate_probe.py`), and the sibling probe
again, to check the 29/32 from hybrid doesn't slip. Only this one thing
changes. No stemming, no weight tuning.

### Stretch result

**What I built:** four lines in `store.py::_fuse_with_bm25`. After fusion
picks the top 5, if the cosine #1 isn't among them, it replaces the fifth.
The baseline was committed before the code (`results/gate_probe_semantic.json`,
`results/gate_probe_hybrid.json`).

#### Run Log — Stretch (third run log)

Raw file: `results/run_2026-09-29_2236_stretch.md` (`run_eval.py::main`,
`run_eval.py::check_out_of_scope`).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Every chunk keeps its title, none under 150 chars | 88 of 88 | 88/88 | 88/88 | 88/88 | MET |
| 5. Cited source is the right file, not a sibling | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |

Retrieved sets for my five questions are identical to the hybrid after-run,
because the semantic #1 was already in the fused top 5 for all of them.
Criterion 3's distances went back to exactly unit 1's (Mongolia 0.869 →
0.825, ibuprofen 0.860 → 0.844, Rust 0.900 → 0.896).

**The failure it targeted, all three modes** (`tools/gate_probe.py`):

| Question | Covered? | Semantic | Hybrid | Hybrid + keep #1 |
|---|---|---|---|---|
| Which dorm is quietest for studying? | Yes | 0.4797 pass | 0.4840 pass | 0.4797 pass |
| How do I get a parking permit? | Yes | 0.5339 pass | 0.5339 pass | 0.5339 pass |
| Where can I print documents? | Yes | 0.6802 pass | **0.7444 REFUSE** | 0.6802 pass |
| Can I bring a car? | Yes | 0.6998 pass | **0.8286 REFUSE** | 0.6998 pass |
| Covered let through | | 4/4 | 2/4 | **4/4** |
| Out-of-scope refused | | 5/5 | 5/5 | 5/5 |

**And the thing hybrid was for didn't slip** (`tools/sibling_probe.py`):
rank 1 on 25/32 (semantic) → 29/32 (hybrid) → 29/32 (hybrid + keep #1).
Exams stay 9/9.

**Real output**, `app.py ask` (via `app.py::ask_pipeline`):

```
$ python app.py ask "Can I bring a car?"
  (best distance 0.700, cutoff 0.7)
Student permits for the west lots go on sale in August, while the east lot never sells out because it is a 12-minute walk. If you miss the permit window, people legally park on Verrill Street and walk in.
Source: admin_parking_permits.txt
Sources retrieved: admin_library_holds.txt, admin_parking_permits.txt, dining_kestrel_commons.txt, dining_verrill_street_grill.txt, housing_fenwick_court.txt

$ python app.py ask "Where can I print documents?"
  (best distance 0.680, cutoff 0.7)
I don't have enough information to answer where you can print documents.
Sources retrieved: admin_library_holds.txt, admin_printing_quota.txt, course_cs_340.txt, money_textbooks.txt, study_library_hours.txt
```

**Did it help?** Yes. It fixed exactly the regression it targeted and cost
nothing measurable. Covered borderline questions went 2/4 → 4/4, back to
semantic's level. The five criteria held at 5/5, and the sibling-probe gain
from hybrid (29/32) stayed. "Can I bring a car?" now gets a real answer
from the parking post. "Where can I print documents?" gets through the gate
again, but the model still declines, as it did in unit 1. So that's a
generation-stage limit (the printing post is about the quota, not a
location), not a retrieval one. What it doesn't fix: hybrid's sibling misses
(CS 340, HIST 118), which this change was never aimed at.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

No criterion is missed after the fix, and none was missed before. So this
section covers what the criteria didn't catch, and that list is real.

1. **Hybrid refuses short, covered questions.** "Where can I print
   documents?" and "Can I bring a car?" went from answered to refused.
   *What I'd do:* make fusion unable to drop the semantic #1. Two parts:
   (a) have the gate judge the best cosine distance over *all* candidates,
   not just the fused top 5; (b) always keep the semantic #1 in the
   results. Secondarily, add stemming and a stopword list to `_tokens`, so
   "print" meets "printing" and "can"/"I"/"a" stop counting as matches.
   *Why I stopped:* the unit allows one change. Stacking a patch on the
   hybrid change would leave the after run measuring two things at once.
   > **Update (Unit 2 stretch):** part (b), keeping the semantic #1, is now
   > built and measured. See "Unit 2 Stretch: A Second Improvement" above.
   > That also delivers (a), since the kept chunk is the one with the best
   > distance. Covered borderline questions are back to 4/4. Stemming and
   > stopwords are still not done.
2. **Two workload siblings still lose (CS 340 at rank 4, HIST 118 not in
   the top 5).** HIST 118's post says "120 pages a week" and never "hours",
   so neither meaning nor keywords links it to the question. *What I'd do:*
   I already have the metadata filter from the unit 1 stretch. If the
   question contains a course code that matches a filename, filter to that
   course's three files before ranking. This is a rule rather than
   learning, but course codes in this corpus are exact and closed-ended.
   *Why I stopped:* same one-change rule, and it's a second retrieval
   change.
3. **Criterion 5 can't score an extra correct sibling.** Both runs cite
   `course_cs_210.txt` next to the expected file, and after hybrid that
   happens on the workload question too. It isn't wrong, since the overview
   repeats the figure, but my criterion has no rule for it. That's a
   criterion fix, not a system fix (see below).
4. **`tools/smoke_test.py` silently overwrites the real index** with fake
   embeddings, which is what broke my first before-run. It shipped with the
   starter, and the fix (point it at a temporary `CHROMA_DIR`) isn't part
   of my system. So I noted it here and re-indexed instead of editing it.

## What I'd Do Differently

- **Criterion 1** would be "the answer's file is at rank 1 for at least
  30 of 32 sibling-probe questions" instead of "in the top 5 for 4 of my 5".
  Five hand-picked questions about entities with distinctive names let the
  course-code weakness hide completely. It only showed up when I asked the
  same question about every course.
- **Criterion 3 was one-sided.** It only tested that the gate refuses what it
  should. I'd add the reverse: "the gate lets through at least 6 of 7
  borderline campus questions the corpus does answer". That's exactly the
  regression hybrid caused, and none of my five criteria could see it.
- **Criterion 5** would say how to count an extra citation: the expected
  file must be named, and any other file named must also contain the fact.
