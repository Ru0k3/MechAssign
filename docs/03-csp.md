# Constraint Satisfaction Problems (CSP)

**Code:** `backend/csp/constraints.py`, `backend/csp/allocator.py`

## 1. The AI concept

A **Constraint Satisfaction Problem** is defined by:

- **Variables** — things we need to assign values to (here: *which shop handles job J*)
- **Domains** — the possible values each variable can take (here: *the set of all shops*)
- **Constraints** — rules restricting which combinations of values are legal (here: *specialty must match, shop must be available, shop must be within range, no shop double-booked*)

Solving a CSP means finding an assignment of a value to every variable that satisfies every constraint. The classic complete algorithm is **backtracking search**: assign one variable at a time, check constraints as soon as enough variables are assigned to evaluate them, and backtrack (undo) the moment a partial assignment becomes unsatisfiable, rather than waiting to generate a full assignment before checking anything. This prunes the search space far below naive brute force.

## 2. The constraints (`constraints.py`)

```python
def matches_specialty(shop, specialist):
    return shop.get("specialty") == specialist

def is_available(entity):
    return entity.get("available", False) is True

def within_max_distance(entity, breakdown, city, maximum):
    locations = node_lookup(city)
    return euclidean(locations[entity["location"]], breakdown) <= maximum
```

These are three independent **unary constraints** — each checks a single variable's candidate value against a fixed property, with no dependency on any other variable's assignment:

| Constraint | Type | Meaning |
|---|---|---|
| `matches_specialty` | Unary, categorical | The shop's declared specialty must equal the specialist type inferred by the knowledge engine (`02-knowledge-representation.md`) |
| `is_available` | Unary, boolean | The shop must not be flagged unavailable in `data/shops.json` |
| `within_max_distance` | Unary, numeric | Straight-line distance from the shop's node to the breakdown point must be ≤ 700 units (default) |

A fourth constraint — **all-different / mutual exclusion** — is **binary across variables**, not unary: no two jobs may be assigned the same shop. It lives in `allocator.py`, not `constraints.py`, because it needs to see the *whole partial assignment*, not just one candidate.

## 3. The solver (`allocator.py`)

### 3.1 Constraint checking for one candidate

```python
def is_valid_choice(job, shop, assignment, city):
    if not matches_specialty(shop, job["specialist_needed"]):
        return False
    if not is_available(shop):
        return False
    if not within_max_distance(shop, job["breakdown_location"], city, job.get("max_distance", 700)):
        return False
    for shop_id in assignment.values():
        if shop_id == shop["id"]:
            return False
    return True
```

This single function is reused by **two different consumers**, which is worth calling out explicitly:

### 3.2 True backtracking search — `backtrack()` / `assign_all_jobs()`

```python
def backtrack(jobs, shops, city, assignment, job_index):
    if job_index == len(jobs):
        return True
    current_job = jobs[job_index]
    for shop in shops:
        if shop["type"] == "shop" and is_valid_choice(current_job, shop, assignment, city):
            assignment[current_job["id"]] = shop["id"]
            if backtrack(jobs, shops, city, assignment, job_index + 1):
                return True
            del assignment[current_job["id"]]          # <-- the "backtrack" step
    return False
```

This is **textbook recursive backtracking**: pick the next unassigned variable (`current_job`), try each value in its domain that currently satisfies all constraints (including the cross-job all-different constraint, since `assignment` already holds every earlier decision), recurse, and if the recursive call fails, **undo the assignment** (`del assignment[...]`) and try the next candidate. This is the general-purpose multi-job CSP solver, able to assign *several simultaneous breakdown jobs* to *distinct* shops.

**Presentation-important nuance:** `assign_all_jobs()` / `backtrack()` are **not called anywhere in the live `/dispatch` pipeline** (`backend/app.py`) and are **not exercised by any test**. They exist in the codebase as the "proper" general CSP solver for the multi-job case, but the running demo only ever solves a single-job allocation (see next section). If you're asked "does this system handle multiple simultaneous breakdowns," the honest answer is: the solver for that case is written and correct, but it isn't wired into the live app — a good thing to flag as a known limitation / future-work hook rather than claim it's active.

### 3.3 What actually runs — `allocate_shop()` / `allocate_store()`

```python
def allocate_shop(shops, specialist, city, breakdown, maximum=700):
    job = {"specialist_needed": specialist, "breakdown_location": breakdown, "max_distance": maximum}
    candidates = []
    for entity in shops:
        if entity["type"] == "shop" and is_valid_choice(job, entity, {}, city):
            candidates.append(entity)
    return candidates
```

Because this is called with a single `job` and an **empty `assignment` dict (`{}`)**, the all-different constraint in `is_valid_choice` is vacuously satisfied (there's nothing in `assignment` to collide with) — so in this single-job case `allocate_shop` degenerates to **pure domain filtering** against the three unary constraints: it returns *every* shop that satisfies specialty + availability + distance, not just one. This is still legitimately "CSP" (it's constraint propagation / domain-filtering, the same idea as unary-constraint pruning in general CSP algorithms like AC-1), it's simply the special case where backtracking never needs to recurse or backtrack because there's only one variable.

`allocate_store()` is the same idea applied to parts stores, with one constraint swapped: instead of `matches_specialty` (equality on one field), it checks **set membership** — `specialist in entity.get("stock", [])` — since a store can stock multiple specialties at once rather than having exactly one.

### 3.4 How the filtered candidates get used

In `run_pipeline()` (`backend/app.py:81-98`):

- **Shops:** *every* CSP-valid candidate is kept, then each one's route is computed via BFS/DFS/A* and the **cheapest-route shop wins** (`04-search-uninformed.md`, `05-search-informed.md`). So shop selection is CSP filtering (feasibility) **followed by** search-based optimization (picking the best of the feasible set) — a very common real-world pattern: constraints define the feasible region, search/optimization picks the best point in it.
- **Stores:** only the **first** CSP-valid candidate (`stores[0]`) is used — no route-cost comparison across store candidates. This asymmetry is real and worth naming if asked why shops get an optimization pass and stores don't: the code simply doesn't run `route_for()` across every store candidate the way it does for shops.

## 4. Presentation talking points

- Three unary constraints (specialty, availability, distance) + one binary all-different constraint = a complete CSP formulation of "assign shops to jobs."
- The repo contains **two** CSP consumers over the same constraint-checking function: a full recursive backtracking solver (`assign_all_jobs`, unused by the live app) and a single-variable domain filter (`allocate_shop`/`allocate_store`, what actually runs). Both are legitimate CSP techniques; only one is in the live path.
- CSP in this project narrows the *feasible set*; it is explicitly **not** the component that picks the *best* one — that's search's job (next two docs).
