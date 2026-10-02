from backend.csp.constraints import matches_specialty, is_available, within_max_distance


def is_valid_choice(job, shop, assignment, city):
    if not matches_specialty(shop, job["specialist_needed"]):
        return False

    if not is_available(shop):
        return False

    if not within_max_distance(shop, job["breakdown_location"], city, job.get("max_distance", 700)):
        return False

    for shop_id in assignment.values():
        if shop_id == shop["id"]:
            return False

    return True


def backtrack(jobs, shops, city, assignment, job_index):
    if job_index == len(jobs):
        return True

    current_job = jobs[job_index]

    for shop in shops:
        if shop["type"] == "shop" and is_valid_choice(current_job, shop, assignment, city):
            assignment[current_job["id"]] = shop["id"]

            if backtrack(jobs, shops, city, assignment, job_index + 1):
                return True

            del assignment[current_job["id"]]

    return False


def assign_all_jobs(jobs, shops, city):
    assignment = {}
    success = backtrack(jobs, shops, city, assignment, 0)
    return assignment if success else None

def allocate_shop(shops, specialist, city, breakdown, maximum=700):
    """Single-job candidate list, built on the same constraint checks as backtracking."""
    job = {"specialist_needed": specialist, "breakdown_location": breakdown, "max_distance": maximum}
    candidates = []
    for entity in shops:
        if entity["type"] == "shop" and is_valid_choice(job, entity, {}, city):
            candidates.append(entity)
    return candidates


def allocate_store(shops, specialist, city, breakdown, maximum=700):
    """Single-job store candidates — matches by stock instead of specialty."""
    candidates = []
    for entity in shops:
        if entity["type"] == "store" and specialist in entity.get("stock", []):
            if is_available(entity) and within_max_distance(entity, breakdown, city, maximum):
                candidates.append(entity)
    return candidates