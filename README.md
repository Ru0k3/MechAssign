# Car Breakdown Dispatch System

A small Flask + SVG application demonstrating explainable classical AI for dispatching a repair technician to a car breakdown.

## Run

```bash
cd car-dispatch-ai
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
python backend/app.py
```

Open <http://127.0.0.1:5000>. Click a corridor in the custom maze, answer the component question, and dispatch a team. The maze is a connected, weighted graph with alternate routes, dead ends, and repair shops and parts depots placed throughout the map. BFS, DFS, and A* compare routes over the same graph. Use **Simulate delay** after a plan is produced to call the replanning endpoint. After the repair is complete, the displayed route is removed automatically after 5 seconds.

## Algorithm map

| File | Technique demonstrated |
|---|---|
| `backend/knowledge/rules.py` | Plain-data rules |
| `backend/knowledge/inference.py` | Forward chaining |
| `backend/csp/constraints.py` | CSP constraints |
| `backend/csp/allocator.py` | Backtracking candidate allocation |
| `backend/search/uninformed.py` | BFS and DFS with frontier traces |
| `backend/search/informed.py` | A* with straight-line heuristic |
| `backend/adversarial.py` | Minimax with alpha-beta pruning |
| `backend/planning/planner.py` | Preconditions and ordered planning |
| `backend/planning/coordinator.py` | ETA synchronization and replanning |
| `backend/app.py` | Flask orchestration and JSON API |
| `frontend/script.js` | SVG interaction and route animation |

## Tests

```bash
python -m pytest -q
```

The tests check that A* is no more costly than BFS on the same route, CSP results have the requested specialty, and repair never becomes ready before both technician and part arrival.
