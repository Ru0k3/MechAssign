from backend.utils.distance import euclidean, node_lookup


def matches_specialty(shop, specialist):
    """Keep only a shop that serves the inferred specialist type."""
    return shop.get("specialty") == specialist


def is_available(entity):
    """Reject unavailable entities."""
    return entity.get("available", False) is True


def within_max_distance(entity, breakdown, city, maximum):
    """Use straight-line distance as a simple CSP bound."""
    locations = node_lookup(city)
    return euclidean(locations[entity["location"]], breakdown) <= maximum
