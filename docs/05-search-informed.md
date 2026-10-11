# Informed Search — A*

**Code:** `backend/search/informed.py`

## 1. The AI concept

**Informed search** uses problem-specific knowledge — a **heuristic function** `h(n)`, an estimate of the cost from node `n` to the goal — to guide exploration toward the goal instead of expanding blindly outward. **A\*** is the canonical informed search algorithm: it expands nodes in order of

```
f(n) = g(n) + h(n)
```

where `g(n)` is the exact cost accumulated so far from the start to `n`, and `h(n)` is the heuristic's estimate of the remaining cost from `n` to the goal. A* is guaranteed to find the optimal (cheapest-cost) path as long as `h` is **admissible** (never overestimates the true remaining cost) — and if `h` is also **consistent**, no node needs to be re-expanded after it's finalized.

## 2. The heuristic — straight-line distance

```python
heuristic = euclidean(locations[neighbor], locations[goal])
```

The heuristic is **Euclidean (straight-line) distance** between a node's `(x, y)` coordinates and the goal's, via `euclidean()` (`backend/utils/distance.py:4`). This is the standard heuristic for route-finding on a 2D map, and it is **admissible here by construction**: every edge's `distance` in `data/city_map.json` is the length of an actual road segment between two points, which by the triangle inequality can never be shorter than the straight-line distance between those same two points. Since straight-line distance is also the shortest possible path through any sequence of intermediate points, the straight-line distance to the goal can never exceed the true cheapest path cost to the goal through the graph — exactly the admissibility condition A* requires.

## 3. The algorithm

```python
def a_star_search(graph, city, start, goal):
    locations = node_lookup(city)
    frontier = []
    heapq.heappush(frontier, (0, start))
    best_cost = {start: 0}            # g(n)
    parent = {start: None}
    expanded = 0
    while frontier:
        priority, current = heapq.heappop(frontier)
        expanded += 1
        if current == goal:
            result = reconstruct_path(parent, start, goal)
            return {"path": result, "cost": path_cost(result, graph), "expanded": expanded}
        for neighbor, edge_cost in graph[current]:
            new_cost = best_cost[current] + edge_cost
            if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                best_cost[neighbor] = new_cost
                heuristic = euclidean(locations[neighbor], locations[goal])
                heapq.heappush(frontier, (new_cost + heuristic, neighbor))
                parent[neighbor] = current
    return {"path": [], "cost": 0, "expanded": expanded}
```

This is a standard A* implementation:

- `best_cost[n]` holds the current best known `g(n)`.
- Every time a cheaper route to `neighbor` is found (`new_cost < best_cost[neighbor]`, or `neighbor` seen for the first time), its `g` value is updated (**relaxation**, the same idea as in Dijkstra's algorithm) and it's pushed onto the frontier with priority `f(n) = g(n) + h(n)`.
- The search terminates the moment `goal` is popped off the frontier — since the frontier is ordered by `f`, and `h` is admissible, the first time `goal` is popped is guaranteed to be via its cheapest-cost route.

**Implementation nuance:** there's no explicit "closed set" check before expanding a node — i.e. no `if current in closed: continue`. Instead, correctness is preserved by the `best_cost` check alone: if a node is popped again later via a stale, higher-priority heap entry, its `g`/`f` have already been finalized by an earlier, cheaper pop, and any neighbor relaxation attempted from that stale entry will simply fail the `new_cost < best_cost[neighbor]` test and do nothing. This is the standard "lazy deletion" pattern for heap-based Dijkstra/A* — it's correct, but it means `expanded` can overcount: a node might be popped (and the counter incremented) more than once if it had multiple stale entries in the heap, even though only its first, cheapest pop actually does useful work.

## 4. Why A* instead of just Dijkstra

Dijkstra's algorithm is exactly A* with `h(n) = 0` for every node — i.e. A* generalizes Dijkstra by adding goal-directed guidance. On this maze graph, Dijkstra would still find the optimal path, but would expand roughly symmetrically outward from `start` in all directions; A*'s heuristic actively steers expansion toward `goal`, usually visiting fewer nodes to reach the same optimal answer. That's exactly what `expanded` is logged for — to let BFS/DFS/A* be compared on "how many nodes did you have to look at to get your answer," not just on path quality.

## 5. Role in the pipeline

`route_for()` (`backend/app.py:55-64`) always uses **A*'s** path and cost as the authoritative route (`astar["path"]`, `astar["cost"]`) — the ETA shown to the user (`astar["cost"] / 50`, treating 50 as a speed constant) and the cost used to compare competing shop candidates (`backend/app.py:87-90`, picking the shop with the lowest `candidate_route["cost"]`) both come from A*, never from BFS or DFS. So A* isn't just displayed for comparison — it's the actual decision-maker behind which route is drawn and which shop is dispatched.

## 6. Presentation talking points

- A* = Dijkstra + a heuristic that's admissible by geometry (straight line ≤ actual road distance) — guaranteed optimal here, not just "usually good."
- `f = g + h` in code: `new_cost + heuristic` is pushed as the priority; `g` is `best_cost`, `h` is `euclidean(...)`.
- A* is the component whose answer actually drives the dispatch decision (shop selection, ETA, drawn route) — BFS/DFS are run purely for the side-by-side pedagogical comparison in the log.
