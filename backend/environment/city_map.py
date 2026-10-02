import json
import os


def load_city_map():
    """Load the graph used by search and the frontend."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "city_map.json")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_graph(city):
    """Build an undirected adjacency list from edge data."""
    graph = {}
    for node in city["nodes"]:
        graph[node["id"]] = []
    for edge in city["edges"]:
        graph[edge["node_a"]].append((edge["node_b"], edge["distance"]))
        graph[edge["node_b"]].append((edge["node_a"], edge["distance"]))
    return graph


def edge_points(city, road_id):
    """Return the coordinates of both endpoints for a selected road."""
    edges = city["edges"]
    nodes = city["nodes"]
    wanted = None
    for edge in edges:
        if edge["road_id"] == road_id:
            wanted = edge
    if wanted is None:
        return None
    first = None
    second = None
    for node in nodes:
        if node["id"] == wanted["node_a"]:
            first = node
        if node["id"] == wanted["node_b"]:
            second = node
    return first, second
