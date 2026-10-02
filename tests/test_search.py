import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.environment.city_map import build_graph, load_city_map
from backend.search.informed import a_star_search
from backend.search.uninformed import breadth_first_search


def test_a_star_cost_is_no_more_than_bfs():
    city = load_city_map()
    graph = build_graph(city)
    start = city["edges"][0]["node_a"]
    goal = city["edges"][0]["node_b"]
    bfs = breadth_first_search(graph, start, goal)
    astar = a_star_search(graph, city, start, goal)
    assert astar["cost"] <= bfs["cost"]


def test_maze_is_connected_and_has_alternate_routes():
    city = load_city_map()
    graph = build_graph(city)
    reached = set()
    pending = [city["nodes"][0]["id"]]

    while pending:
        current = pending.pop()
        if current in reached:
            continue
        reached.add(current)
        pending.extend(neighbor for neighbor, _ in graph[current] if neighbor not in reached)

    assert len(reached) == len(city["nodes"])
    assert len(city["edges"]) > len(city["nodes"]) - 1
    assert any(len(neighbors) == 1 for neighbors in graph.values())


def test_dispatch_returns_routes_on_the_maze():
    from backend.app import app

    city = load_city_map()
    edge = city["edges"][0]
    nodes = {node["id"]: node for node in city["nodes"]}
    first = nodes[edge["node_a"]]
    second = nodes[edge["node_b"]]
    response = app.test_client().post(
        "/dispatch",
        json={
            "road_id": edge["road_id"],
            "position": {
                "x": (first["x"] + second["x"]) / 2,
                "y": (first["y"] + second["y"]) / 2,
            },
            "damage_type": "engine",
            "answers": {"follow_up": "yes"},
            "has_part": False,
        },
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["shop_route"]["path"]
    assert result["logs"]
