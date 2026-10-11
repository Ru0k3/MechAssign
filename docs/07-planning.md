# Planning — Ordered Actions, Preconditions, and Replanning

**Code:** `backend/planning/planner.py`, `backend/planning/coordinator.py`

## 1. The AI concept

**Classical (STRIPS-style) planning** represents a task as a sequence of **actions**, each with:

- **Preconditions** — facts that must hold before the action can legally execute
- **Effects** — facts the action makes true/false once it executes

A **plan** is a sequence of actions whose preconditions are satisfied *given the effects of the actions before it* — a totally ordered plan assumes one fixed sequence works for the whole execution. In dynamic/real-world execution, the agent also needs **execution monitoring** (checking, at run time, whether an action's preconditions actually hold before committing to it) and **replanning** (repairing or recomputing the plan when the world didn't go as expected — e.g. something arrives late).

This project demonstrates both halves: `planner.py` builds the ordered action sequence and checks one real precondition live; `coordinator.py` handles multi-resource timing synchronization and reactive replanning after a delay.

## 2. The plan — `planner.py`

```python
ACTIONS = ["diagnose", "assign shop", "assign store", "travel", "repair", "verify", "close"]

def build_plan(parts_needed, technician_arrived=False, part_arrived=False):
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
        step_number += 1
    return steps
```

- **The action sequence itself is fixed** (`ACTIONS`), not derived by searching over a state space of possible orderings — this is "plan representation + precondition checking," not "plan synthesis" (the project doesn't run a GraphPlan/STRIPS-search style algorithm to *discover* that "diagnose" must precede "repair"; that ordering is simply hand-authored). Worth being precise about this if asked whether the system "plans" in the search sense — it doesn't search for a plan, it monitors and conditionally gates a predetermined one.
- **Conditional step inclusion:** the `"assign store"` step is skipped entirely when `parts_needed` is false — a simple form of conditional planning, where the applicable action set depends on the current problem instance's facts.
- **Precondition checking happens for exactly one action, "repair":** `ready = technician_arrived and (part_arrived or not parts_needed)`. In STRIPS terms, `repair`'s precondition is "technician has arrived AND (a part has arrived OR no part was ever needed)." Every other action in the list is marked `preconditions_met: True` unconditionally — the plan models real precondition logic specifically where it matters most (you cannot repair the car before both the person and the part needed to do the repair are on site), rather than modeling every action's preconditions exhaustively.

## 3. Synchronizing two resources — `coordinator.py`

```python
def coordinate(technician_eta, parts_eta):
    delay = technician_eta - parts_eta
    if delay < 0:
        delay = 0
    parts_delay = 0
    technician_delay = 0
    if technician_eta < parts_eta:
        technician_delay = parts_eta - technician_eta
    else:
        parts_delay = technician_eta - parts_eta
    ...
    return {"technician_eta": technician_eta, "parts_eta": parts_eta,
            "dispatch_delay": delay, "technician_delay": technician_delay,
            "parts_delay": parts_delay, "log": message}
```

The repair can't start until **both** the technician and the part have arrived — the ready time for `repair` is effectively `max(technician_eta, parts_eta)`. `coordinate()` figures out which of the two is the bottleneck and reports how long the *other* one will sit waiting (`technician_delay` or `parts_delay`), plus a `dispatch_delay` figure (how much later than the parts' arrival the technician arrives, floored at 0). This is a small instance of **multi-agent / multi-resource plan synchronization** — a recurring theme in real planning systems where a goal depends on multiple independent resources converging, and the plan has to account for whichever one is slower.

## 4. Reactive replanning — `coordinator.replan()`

```python
def replan(plan, completed_actions, reason, technician_eta=None, parts_eta=None, delay_minutes=0):
    remaining = [step for step in plan if step["action"] not in completed_actions]
    updated_coordination = None
    if delay_minutes > 0 and technician_eta is not None and parts_eta is not None:
        updated_coordination = coordinate(technician_eta + delay_minutes, parts_eta)
    ...
    return {"steps": remaining, "log": message, "updated_coordination": updated_coordination}
```

This models the **sense → plan → act → (unexpected event) → replan** loop central to planning in dynamic environments:

1. **Plan repair by subtraction:** rather than regenerating a plan from scratch, `replan` simply drops whatever actions are already `completed_actions` from the original plan and keeps the rest — the cheapest possible form of replanning (no search, just filtering), appropriate because nothing about the *remaining* actions' ordering needs to change, only which ones are left to do.
2. **Re-coordination:** if a `delay_minutes` is supplied, the technician's ETA is pushed back by that amount and `coordinate()` is re-run on the new ETAs — so the repair-ready time, bottleneck, and wait figures are all recomputed against the new reality.

This is triggered from the frontend's **"Simulate delay"** button (`frontend/script.js:136`), which calls `POST /simulate-delay` with `completed_actions: ['diagnose', 'assign shop']` and a fixed `delay_minutes: 10` hardcoded in the frontend, to narrate "the technician got held up at a previous job, by 10 minutes — here's the replanned ETA and remaining steps." The backend endpoint (`backend/app.py:142`) just forwards the payload into `replan()` — it does not re-run inference, CSP, or search at all on replan; only the planning/coordination stage re-executes.

## 5. Presentation talking points

- Two planning ideas kept deliberately separate: (a) a **fixed action sequence with one real STRIPS-style precondition check** (`repair` needs technician + part), and (b) **multi-resource ETA synchronization + reactive replanning** when a delay happens mid-execution.
- This system does **not** search for a plan (no GraphPlan/backward-chaining over STRIPS operators) — the ordering is authored, not synthesized. That's an accurate and important distinction if you're asked "did you implement an actual planning algorithm."
- Replanning here is "drop completed steps + recompute timing," the simplest valid form of plan repair — contrast this with full replanning (recomputing an entirely new plan from the current state), which this project doesn't need because the remaining action sequence never actually changes, just its readiness/timing.
