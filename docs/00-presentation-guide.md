# Presentation Guide — Talking Points

A slide-by-slide-ready distillation of `01`–`09`. Use this as the script; use the numbered docs for the depth behind each point.

## Suggested order

1. **Hook / framing (1 slide):** "This is a classical-AI system — no machine learning. Every decision is a named, textbook AI technique, and every one of them prints its own reasoning trace, so nothing is a black box." → `01-overview.md §1-2`
2. **The pipeline (1 slide, show the mermaid diagram):** one request flows through 6 AI stages in a fixed order. → `01-overview.md §3`
3. **Problem formulation (1 slide):** state space = weighted graph of 38 nodes / 45 edges, with a guaranteed dead end and alternate routes so the search algorithms can meaningfully disagree. → `01-overview.md §4`
4. **Knowledge representation & forward chaining (1-2 slides):** rules as data, not code; two-hop chain (base rule → severity-escalation rule reading the base rule's own output). → `02-knowledge-representation.md`
5. **CSP (1-2 slides):** 3 unary constraints + 1 binary all-different constraint; show both the single-job filter (what runs) and the full backtracking solver (what's implemented but dormant) as two valid CSP strategies. → `03-csp.md`
6. **Uninformed search (1 slide):** BFS/DFS run side-by-side with A* purely to compare expansion counts and path quality in the live log. → `04-search-uninformed.md`
7. **Informed search (1 slide):** A* is the one that actually decides the route/ETA/shop ranking; heuristic is provably admissible (straight-line ≤ real road distance). → `05-search-informed.md`
8. **Adversarial search (1-2 slides):** 2-ply minimax tree + alpha-beta pruning deciding which of two competing jobs goes first; show the tree diagram. → `06-adversarial-search.md`
9. **Planning (1-2 slides):** fixed action sequence + one real STRIPS precondition (`repair` needs technician + part); ETA synchronization; replanning by dropping completed steps and recomputing timing after a delay. → `07-planning.md`
10. **Frontend (1 slide, brief):** pure visualization, zero AI logic, just renders what the backend decided. → `08-frontend.md`
11. **Wrap-up / comparison table (1 slide):** show `09-comparison-tables.md`'s "what each stage answers" table as a one-glance summary of the whole system.

## One-liners per technique (good for slide captions)

- **Forward chaining:** "Facts flow forward — an early rule's conclusion becomes a later rule's input."
- **CSP:** "Narrow the feasible set first (who's even eligible), then let search pick the best of what's left."
- **BFS:** "Fewest hops, guaranteed — but not necessarily the shortest *distance*."
- **DFS:** "Plunges to full depth before backtracking — no optimality guarantee, demonstrated for contrast."
- **A\*:** "Dijkstra plus a goal-directed heuristic that's provably admissible here — this is the one that actually drives the dispatch."
- **Minimax + alpha-beta:** "Plan for the worst case the 'opponent' (here: urgency escalation) could force, and skip branches that are already provably worse."
- **Planning:** "A fixed, hand-authored action sequence with one real precondition gate — the system monitors readiness, it doesn't search for the plan."
- **Replanning:** "The cheapest valid repair: drop what's done, recompute timing, don't regenerate what hasn't changed."

## Things to be ready to say honestly if pressed

These are real, verified-in-code facts (see `09-comparison-tables.md`'s "known gaps" table) — own them rather than getting caught out:

- The full multi-job CSP backtracking solver (`assign_all_jobs`) exists and is correct, but the live demo only ever solves the single-job case; it isn't wired into `/dispatch` and has no test coverage.
- The adversarial/minimax stage currently compares the real request against a placeholder (urgency 0), so in practice it almost always "decides" to serve the real request — the mechanism (tree, pruning) is real and demonstrable, the decision itself isn't currently load-bearing.
- Parts-store selection takes the first CSP-eligible store rather than optimizing its route cost the way shop selection does.
- Planning here does not *search* for a plan (no GraphPlan-style synthesis) — the action order is authored by hand; what's dynamic is the precondition/readiness check and the replanning-by-subtraction step.

These are good "depth of understanding" answers if a question tries to probe whether the system does more than it does — the honest, specific answer is stronger than overclaiming.
