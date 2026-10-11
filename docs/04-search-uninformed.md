# Uninformed Search — BFS and DFS

**Code:** `backend/search/uninformed.py`

## 1. The AI concept

**Uninformed (blind) search** explores a state space using only the problem's structure (the graph) — it has no extra information (no heuristic) about which direction looks promising. The two classics:

| Algorithm | Frontier structure | Explores by | Complete? | Optimal? |
|---|---|---|---|---|
| **BFS** (Breadth-First Search) | FIFO queue | Shallowest nodes first (level by level) | Yes (finite graph) | Yes, *for unweighted edge count* — not necessarily for weighted cost |
| **DFS** (Depth-First Search) | LIFO stack | Deepest nodes first (plunges down one branch before backtracking) | Yes (finite graph) | No |

## 2. Shared helpers

```python
def reconstruct_path(parent, start, goal):
    """Follow parent links backward and return the route in forward order."""
```
Both BFS and DFS record a `parent` pointer each time they discover a node, then `reconstruct_path` walks `goal → ... → start` backward through `parent` and reverses it. If `goal` was never reached, it returns `[]`.

```python
def path_cost(path, graph):
    """Add edge weights along a route."""
```
This sums the actual weighted edge distances along the reconstructed path — note this is computed **after** the search finishes, purely for reporting/comparison. It is not the quantity BFS/DFS are searching to minimize (see below).

## 3. Breadth-First Search

```python
def breadth_first_search(graph, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    parent = {start: None}
    depth = {start: 0}
    expanded = 0
    while frontier:
        current_depth, current = heapq.heappop(frontier)
        expanded += 1
        if current == goal:
            result = reconstruct_path(parent, start, goal)
            return {"path": result, "cost": path_cost(result, graph), "expanded": expanded}
        for neighbor, unused_cost in graph[current]:
            if neighbor not in depth:
                depth[neighbor] = current_depth + 1
                parent[neighbor] = current
                heapq.heappush(frontier, (depth[neighbor], neighbor))
    return {"path": [], "cost": 0, "expanded": expanded}
```

**Implementation detail:** this isn't built on `collections.deque` the way textbook BFS usually is — it's built on a `heapq` **min-priority-queue keyed by depth** (`unused_cost`, the edge weight, is explicitly discarded). Because every node is pushed with priority `depth+1` relative to its parent, and depths only ever increase by exactly 1 per hop, the heap pops nodes in non-decreasing depth order — the same effective expansion order a FIFO queue would give. So it *is* correct BFS (shallowest-first), just implemented with a heap instead of a deque, presumably to share a consistent "frontier = heap of (priority, node)" shape with DFS and A* in the same module/sibling module.

**Important nuance for Q&A:** BFS here finds the path with the **fewest edges (hops)**, because `depth` counts hops, not the fewest-*weighted-cost* path. `path_cost` is computed afterward just to report what that hop-shortest path happens to cost in real distance — but on a weighted graph, the fewest-hop path is not guaranteed to be the cheapest-distance path. BFS is optimal with respect to edge count, not necessarily with respect to the `distance` weights used elsewhere in this project. (Compare to A*, `05-search-informed.md`, which does optimize true weighted cost.)

## 4. Depth-First Search

```python
def depth_first_search(graph, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    parent = {start: None}
    visited = {}
    expanded = 0
    while frontier:
        priority, current = heapq.heappop(frontier)
        if current in visited:
            continue
        visited[current] = True
        expanded += 1
        if current == goal:
            result = reconstruct_path(parent, start, goal)
            return {"path": result, "cost": path_cost(result, graph), "expanded": expanded}
        neighbors = graph[current]
        index = len(neighbors) - 1
        while index >= 0:
            neighbor, unused_cost = neighbors[index]
            if neighbor not in visited:
                parent[neighbor] = current
                heapq.heappush(frontier, (priority - 1, neighbor))
            index -= 1
    return {"path": [], "cost": 0, "expanded": expanded}
```

Here the heap priority is **decremented by 1 every level** (`priority - 1`), so deeper nodes always carry a *more negative* priority than their ancestors or un-expanded siblings and therefore always pop first — this simulates a LIFO stack's "always continue down the branch you just extended" behavior using a min-heap instead of an explicit stack. `visited` acts as the usual DFS closed set, and stale duplicate heap entries for an already-visited node are simply skipped (`if current in visited: continue`) rather than filtered out of the heap — a standard lazy-deletion trick.

**Implementation subtlety worth knowing (but not over-claiming in a presentation):** the neighbor loop iterates `index` from `len(neighbors) - 1` down to `0` — the classic "push in reverse so the first neighbor in adjacency order ends up popped first" trick used with an actual stack. But because the frontier here is a **heap of `(priority, neighbor_id)` tuples**, and all neighbors pushed in the same loop iteration share the *same* `priority - 1` value, ties are broken by Python's tuple comparison on the second element — i.e. **alphabetically by node id**, not by push order. So the reverse-iteration trick has no effect on sibling order here; which sibling is explored first is actually decided by node-id ordering, not adjacency-list order. The algorithm is still correct DFS (it still plunges to full depth before backtracking), just with alphabetical tie-breaking among siblings rather than adjacency-order tie-breaking. A fine thing to mention if someone asks "why does it visit N9 before N16 instead of the other way around."

## 5. What the pipeline does with both

`route_for()` (`backend/app.py:55`) runs **BFS, DFS, and A* on the exact same graph and endpoints** for every shop/store candidate, purely so their `expanded`/`cost` numbers can be compared and logged side by side — the actual route that gets drawn and whose ETA is used downstream is always **A*'s** (`backend/app.py:64`, `astar["path"]`/`astar["cost"]`). BFS and DFS results are computed and printed to the trace log for pedagogical contrast but don't otherwise affect the dispatch decision.

## 6. Presentation talking points

- BFS = shallowest-first, guarantees fewest *hops*; DFS = deepest-first, guarantees neither hops nor cost, can be badly suboptimal, but uses far less memory than BFS on wide graphs (stores only the current branch, not a whole frontier level) — though this particular implementation doesn't take advantage of that, since both share the same `heapq`-based frontier pattern.
- Both are implemented on a shared heap-based frontier even though a plain queue/stack would be the textbook choice — the heap's priority value (ascending depth vs. descending depth) is what encodes "breadth-first" vs. "depth-first" here, which is a nice "same data structure, different priority function" teaching point if you want one.
- `tests/test_search.py` deliberately builds a maze with alternate routes *and* a dead end (`any(len(neighbors) == 1 ...)`) specifically so BFS/DFS/A* can be shown disagreeing on which path they return.
