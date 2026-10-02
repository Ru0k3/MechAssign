import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.csp.allocator import allocate_shop
from backend.environment.city_map import load_city_map


def test_csp_returns_only_matching_specialty():
    root = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(root, "data", "shops.json"), "r", encoding="utf-8") as file:
        shops = json.load(file)
    city = load_city_map()
    candidates = allocate_shop(shops, "brakes", city, {"x": 240, "y": 230})
    assert len(candidates) > 0
    for candidate in candidates:
        assert candidate["specialty"] == "brakes"
