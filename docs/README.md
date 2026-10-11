# Documentation Index

Docs for the Car Breakdown Dispatch System, written for presentation prep on **Fundamentals of AI**. Each AI technique in the codebase gets its own file: general concept, then a line-by-line mapping to this project's implementation, plus honest notes on what's actually wired into the live demo versus what's implemented but dormant.

| # | File | Covers |
|---|---|---|
| 00 | [00-presentation-guide.md](00-presentation-guide.md) | Slide-by-slide talking points, one-liners, and the "known gaps" to be ready for in Q&A |
| 01 | [01-overview.md](01-overview.md) | What the system does, the request pipeline, problem formulation (state space), file map |
| 02 | [02-knowledge-representation.md](02-knowledge-representation.md) | Rule-based knowledge base + forward chaining inference |
| 03 | [03-csp.md](03-csp.md) | Constraint satisfaction: constraints, backtracking search, domain filtering |
| 04 | [04-search-uninformed.md](04-search-uninformed.md) | BFS and DFS |
| 05 | [05-search-informed.md](05-search-informed.md) | A* with an admissible straight-line heuristic |
| 06 | [06-adversarial-search.md](06-adversarial-search.md) | Minimax with alpha-beta pruning |
| 07 | [07-planning.md](07-planning.md) | Ordered actions, STRIPS-style preconditions, ETA coordination, replanning |
| 08 | [08-frontend.md](08-frontend.md) | Brief note on the SVG/JS frontend (visualization only, no AI logic) |
| 09 | [09-comparison-tables.md](09-comparison-tables.md) | Cross-cutting comparison tables for quick reference/slides |

**Suggested reading order for presentation prep:** `00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09`, i.e. start with the talking points for structure, then read the overview for the big picture, then follow the pipeline stage by stage in the order it actually executes.
