import contextlib
import io
import json
import os
import sys
from flask import Flask, jsonify, request, send_from_directory

# Add the project root so direct execution can import the backend package.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.adversarial import choose_request
from backend.csp.allocator import allocate_shop, allocate_store
from backend.environment.city_map import build_graph, edge_points, load_city_map
from backend.knowledge.inference import infer_facts
from backend.knowledge.questions import QUESTIONS
from backend.planning.coordinator import coordinate, replan
from backend.planning.planner import build_plan
from backend.search.informed import a_star_search
from backend.search.uninformed import breadth_first_search, depth_first_search

ROOT = PROJECT_ROOT
DATA = os.path.join(ROOT, "data")
FRONTEND = os.path.join(ROOT, "frontend")
app = Flask(__name__, static_folder=FRONTEND, static_url_path="/static")

with open(os.path.join(DATA, "shops.json"), "r", encoding="utf-8") as file:
    SHOPS = json.load(file)
CITY = load_city_map()
GRAPH = build_graph(CITY)


def find_node_for_position(road_id, position):
    """Choose the closer road endpoint as the graph goal for routing."""
    endpoints = edge_points(CITY, road_id)
    if endpoints is None:
        return None
    first, second = endpoints
    first_distance = (position["x"] - first["x"]) ** 2 + (position["y"] - first["y"]) ** 2
    second_distance = (position["x"] - second["x"]) ** 2 + (position["y"] - second["y"]) ** 2
    if first_distance <= second_distance:
        return first["id"]
    return second["id"]


def find_entity(entity_id):
    """Find a shop or store by its stable identifier."""
    for entity in SHOPS:
        if entity["id"] == entity_id:
            return entity
    return None


def route_for(entity, goal):
    """Run all required searches and return their comparable results."""
    start = entity["location"]
    bfs = breadth_first_search(GRAPH, start, goal)
    dfs = depth_first_search(GRAPH, start, goal)
    astar = a_star_search(GRAPH, CITY, start, goal)
    print("[BFS] ended nodes expanded: " + str(bfs["expanded"]) + ", cost: " + str(bfs["cost"]))
    print("[DFS] ended nodes expanded: " + str(dfs["expanded"]) + ", cost: " + str(dfs["cost"]))
    print("[A*] ended nodes expanded: " + str(astar["expanded"]) + ", cost: " + str(astar["cost"]))
    return {"bfs": bfs, "dfs": dfs, "astar": astar, "path": astar["path"], "cost": astar["cost"], "eta": astar["cost"] / 50}


def run_pipeline(payload):
    """Run the requested classical-AI stages in their specified order."""
    road_id = payload.get("road_id")
    position = payload.get("position", {})
    damage_type = payload.get("damage_type")
    answers = payload.get("answers", {})
    has_part = bool(payload.get("has_part", False))
    goal = find_node_for_position(road_id, position)
    if goal is None:
        raise ValueError("Unknown road_id")
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        facts = infer_facts(damage_type, answers, has_part)
        breakdown = {"x": position["x"], "y": position["y"]}
        shop_candidates = allocate_shop(SHOPS, facts["specialist_needed"], CITY, breakdown)
        if len(shop_candidates) == 0:
            raise ValueError("No technician satisfies the CSP")
        best_shop = None
        best_route = None
        for candidate in shop_candidates:
            candidate_route = route_for(candidate, goal)
            if best_route is None or candidate_route["cost"] < best_route["cost"]:
                best_shop = candidate
                best_route = candidate_route
        store = None
        store_route = None
        if facts["parts_needed"]:
            stores = allocate_store(SHOPS, facts["specialist_needed"], CITY, breakdown)
            if len(stores) == 0:
                raise ValueError("No parts store satisfies the CSP")
            store = stores[0]
            store_route = route_for(store, goal)
        conflict = choose_request(
            {"id": "current", "urgency": facts["urgency"]},
            {"id": "other", "urgency": 0},
        )
        plan = build_plan(facts["parts_needed"])
        coordination = coordinate(best_route["eta"], store_route["eta"] if store_route else best_route["eta"])
    log_lines = stream.getvalue().splitlines()
    return {"facts": facts, "goal_node": goal, "shop": best_shop, "shop_route": best_route, "store": store, "store_route": store_route, "conflict": conflict, "plan": plan, "coordination": coordination, "logs": log_lines, "city": CITY}


@app.get("/")
def index():
    """Serve the single-page dispatch interface."""
    return send_from_directory(FRONTEND, "index.html")


@app.get("/api/questions")
def questions():
    """Expose the knowledge-base follow-up questions."""
    return jsonify(QUESTIONS)


@app.get("/api/city")
def city_data():
    """Expose map data needed to draw the SVG."""
    return jsonify(CITY)


@app.get("/api/entities")
def entity_data():
    """Expose shops and stores needed for map labels."""
    return jsonify(SHOPS)


@app.post("/dispatch")
def dispatch():
    """Validate a request and return the complete explainable dispatch plan."""
    try:
        return jsonify(run_pipeline(request.get_json(force=True)))
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400


@app.post("/simulate-delay")
def simulate_delay():
    """Replan only the remaining actions after a user-simulated delay."""
    payload = request.get_json(force=True)
    completed = payload.get("completed_actions", [])
    reason = payload.get("reason", "simulated technician delay")
    technician_eta = payload.get("technician_eta")
    parts_eta = payload.get("parts_eta")
    delay_minutes = payload.get("delay_minutes", 0)
    result = replan(payload.get("plan", []), completed, reason, technician_eta, parts_eta, delay_minutes)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
