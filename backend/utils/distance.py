import math


def euclidean(first, second):
    """Return straight-line distance between two coordinate dictionaries."""
    dx = first["x"] - second["x"]
    dy = first["y"] - second["y"]
    return math.sqrt(dx * dx + dy * dy)


def node_lookup(city):
    """Create a lookup table for graph node coordinates."""
    result = {}
    for node in city["nodes"]:
        result[node["id"]] = node
    return result
