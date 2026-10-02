import heapq


def reconstruct_path(parent, start, goal):
    """Follow parent links backward and return the route in forward order."""
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    if len(path) == 0 or path[0] != start:
        return []
    return path


def path_cost(path, graph):
    """Add edge weights along a route."""
    total = 0
    index = 0
    while index < len(path) - 1:
        first = path[index]
        second = path[index + 1]
        for neighbor, cost in graph[first]:
            if neighbor == second:
                total += cost
        index += 1
    return total


def breadth_first_search(graph, start, goal):
    """Search by shallowest depth while recording every popped node."""
    print("[BFS] started")
    frontier = []
    heapq.heappush(frontier, (0, start))
    parent = {start: None}
    depth = {start: 0}
    expanded = 0
    while frontier:
        current_depth, current = heapq.heappop(frontier)
        print("Popped node: " + str(current) + " with cost " + str(current_depth))
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


def depth_first_search(graph, start, goal):
    """Search deeply first using a negative depth heap priority."""
    print("[DFS] started")
    frontier = []
    heapq.heappush(frontier, (0, start))
    parent = {start: None}
    visited = {}
    expanded = 0
    while frontier:
        priority, current = heapq.heappop(frontier)
        print("Popped node: " + str(current) + " with cost " + str(-priority))
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


if __name__ == "__main__":
    sample = {"A": [("B", 1)], "B": [("A", 1), ("C", 1)], "C": [("B", 1)]}
    print(breadth_first_search(sample, "A", "C"))
    print(depth_first_search(sample, "A", "C"))
