# Comparison Tables

Quick-reference tables for slides — cross-cutting comparisons across the techniques covered in `02`–`07`.

## Search algorithms

| | BFS | DFS | A* |
|---|---|---|---|
| Frontier structure | Min-heap keyed by depth (acts as FIFO) | Min-heap keyed by negated depth (acts as LIFO) | Min-heap keyed by `f = g + h` |
| Uses a heuristic? | No | No | Yes — Euclidean distance to goal |
| Optimal for... | Fewest edges (hops) | Nothing guaranteed | True weighted path cost (admissible heuristic) |
| Complete (finds a path if one exists)? | Yes | Yes | Yes |
| Typical nodes expanded | Moderate (expands by level) | Can be low or high depending on branch order | Lowest of the three, thanks to goal-directed guidance |
| Drives the actual dispatch decision? | No — logged for comparison only | No — logged for comparison only | **Yes** — its path/cost is what's used for ETA and shop ranking |
| Code | `backend/search/uninformed.py` | `backend/search/uninformed.py` | `backend/search/informed.py` |

## Reasoning / decision techniques

| Technique | Category | Input | Output | Code |
|---|---|---|---|---|
| Forward chaining | Knowledge representation & inference | `damage_type`, follow-up answer, `has_part` | `specialist_needed`, `parts_needed`, `urgency` | `backend/knowledge/inference.py` |
| CSP domain filtering | Constraint satisfaction | Specialty needed, breakdown location | List of shops/stores satisfying all constraints | `backend/csp/allocator.py` (`allocate_shop`, `allocate_store`) |
| CSP backtracking search | Constraint satisfaction | Multiple jobs + shop pool | A conflict-free job→shop assignment (unused in live pipeline) | `backend/csp/allocator.py` (`backtrack`, `assign_all_jobs`) |
| Minimax + alpha-beta | Adversarial / worst-case decision-making | Two requests' urgencies | Which to serve first, plus pruning count | `backend/adversarial.py` |
| Ordered planning + precondition check | Classical planning | `parts_needed`, arrival flags | Ordered action list with readiness per step | `backend/planning/planner.py` |
| ETA coordination + replanning | Plan execution monitoring / repair | Technician & parts ETAs, optional delay | Bottleneck, wait times, remaining steps | `backend/planning/coordinator.py` |

## CSP vs. search vs. planning — what each one is responsible for

| Stage | Answers the question... | Technique |
|---|---|---|
| Knowledge/inference | "What's actually wrong, and how urgent is it?" | Rule-based forward chaining |
| CSP | "Which shops/stores are even *eligible* to take this job?" | Constraint filtering / backtracking |
| Search (BFS/DFS/A*) | "Of the eligible ones, which is *fastest to reach* — and how do different strategies compare?" | Graph search |
| Adversarial | "If two jobs were competing for attention, which should go first?" | Minimax + alpha-beta |
| Planning | "What's the correct order of steps, and is each one allowed to start yet?" | STRIPS-style ordered plan + precondition check |
| Coordination/replanning | "When do both resources converge, and what happens if one is delayed?" | Timing synchronization + reactive plan repair |

## Known gaps between "what's implemented" and "what's wired into the live demo"

Useful to have ready for Q&A — these are accurate, verified-in-code observations, not guesses:

| Component | Status |
|---|---|
| `assign_all_jobs` / `backtrack` (multi-job CSP backtracking) | Implemented correctly, never called by `app.py`, no test coverage |
| `backend/environment/entities.py` (`Request`, `Assignment` classes) | Defined, never imported/instantiated anywhere — `app.py` uses plain dicts instead |
| `facts` dict in `infer_facts()` | Built, never returned — only `derived` is |
| Store selection (`allocate_store` → first match) | Not cost-optimized across candidates, unlike shop selection which picks the cheapest A* route among CSP-valid candidates |
| `choose_request()` in the live pipeline | Always compares the real request against a placeholder of urgency `0`, so the real request wins almost every time — the function itself is general-purpose, the demo just doesn't feed it two real competing requests |
