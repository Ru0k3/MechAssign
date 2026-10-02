def coordinate(technician_eta, parts_eta):
    """Delay the faster party so both arrive at the same time."""
    delay = technician_eta - parts_eta
    if delay < 0:
        delay = 0
    parts_delay = 0
    technician_delay = 0
    if technician_eta < parts_eta:
        technician_delay = parts_eta - technician_eta
    else:
        parts_delay = technician_eta - parts_eta
    message = "[COORDINATOR] technician ETA=" + str(technician_eta) + ", parts ETA=" + str(parts_eta) + ", dispatch delay=" + str(delay)
    print(message)
    return {"technician_eta": technician_eta, "parts_eta": parts_eta, "dispatch_delay": delay, "technician_delay": technician_delay, "parts_delay": parts_delay, "log": message}


def replan(plan, completed_actions, reason, technician_eta=None, parts_eta=None, delay_minutes=0):
    """Recompute remaining steps, and re-coordinate timing if a delay occurred."""
    remaining = []
    for step in plan:
        if step["action"] not in completed_actions:
            remaining.append(step)

    updated_coordination = None
    if delay_minutes > 0 and technician_eta is not None and parts_eta is not None:
        updated_coordination = coordinate(technician_eta + delay_minutes, parts_eta)

    message = "[REPLAN] reason: " + reason + ", remaining steps: " + str([item["action"] for item in remaining])
    print(message)
    return {"steps": remaining, "log": message, "updated_coordination": updated_coordination}