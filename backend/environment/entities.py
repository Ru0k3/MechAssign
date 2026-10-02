class Request:
    """Hold the facts supplied by one breakdown request."""
    def __init__(self, damage_type, answers, has_part, road_id, position):
        self.damage_type = damage_type
        self.answers = answers
        self.has_part = has_part
        self.road_id = road_id
        self.position = position


class Assignment:
    """Hold one selected technician or parts store."""
    def __init__(self, entity, path, cost):
        self.entity = entity
        self.path = path
        self.cost = cost
