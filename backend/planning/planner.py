ACTIONS = ["diagnose", "assign shop", "assign store", "travel", "repair", "verify", "close"]


def build_plan(parts_needed, technician_arrived=False, part_arrived=False):
    """Create an ordered plan and mark whether each action can start."""
    steps = []
    step_number = 1
    for action in ACTIONS:
        if action == "assign store" and not parts_needed:
            continue
        ready = True
        if action == "repair":
            ready = technician_arrived and (part_arrived or not parts_needed)
        entry = {"step": step_number, "action": action, "preconditions_met": ready}
        steps.append(entry)
        print("[PLANNER] step " + str(step_number) + ": " + action + " (preconditions met: " + ("yes" if ready else "no") + ")")
        step_number += 1
    return steps


if __name__ == "__main__":
    print(build_plan(True))