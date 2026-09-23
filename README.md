# The Unofficial Guide

Austin Stanley Hinson — corpus: `campus_life` (88 short student posts about dining, housing, courses and campus admin).

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

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

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

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
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

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

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
