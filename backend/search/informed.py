import heapq
from backend.search.uninformed import reconstruct_path, path_cost
from backend.utils.distance import euclidean, node_lookup


def a_star_search(graph, city, start, goal):
    """Find a low-cost route using straight-line distance as the heuristic."""
    print("[A*] started")
    locations = node_lookup(city)
    frontier = []
    heapq.heappush(frontier, (0, start))
    best_cost = {start: 0}
    parent = {start: None}
    expanded = 0
    while frontier:
        priority, current = heapq.heappop(frontier)
        print("Popped node: " + str(current) + " with cost " + str(best_cost[current]))
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
