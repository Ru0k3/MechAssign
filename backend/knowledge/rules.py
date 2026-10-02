DAMAGE_TYPES = ["engine", "brakes", "window/glass", "tires", "exhaust", "internal parts", "electronics"]

RULES = [
    {"when": {"damage_type": "engine"}, "then": {"specialist_needed": "engine", "parts_needed": True, "urgency": 5}},
    {"when": {"damage_type": "brakes"}, "then": {"specialist_needed": "brakes", "parts_needed": True, "urgency": 5}},
    {"when": {"damage_type": "window/glass"}, "then": {"specialist_needed": "window/glass", "parts_needed": True, "urgency": 3}},
    {"when": {"damage_type": "tires"}, "then": {"specialist_needed": "tires", "parts_needed": True, "urgency": 4}},
    {"when": {"damage_type": "exhaust"}, "then": {"specialist_needed": "exhaust", "parts_needed": True, "urgency": 2}},
    {"when": {"damage_type": "internal parts"}, "then": {"specialist_needed": "internal parts", "parts_needed": True, "urgency": 3}},
    {"when": {"damage_type": "electronics"}, "then": {"specialist_needed": "electronics", "parts_needed": True, "urgency": 3}}
]
