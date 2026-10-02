import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.planning.planner import build_plan


def test_repair_waits_for_technician_and_part():
    plan = build_plan(True, technician_arrived=False, part_arrived=False)
    repairs = [step for step in plan if step["action"] == "repair"]
    assert len(repairs) == 1
    assert repairs[0]["preconditions_met"] is False


def test_repair_is_ready_when_both_arrive():
    plan = build_plan(True, technician_arrived=True, part_arrived=True)
    repairs = [step for step in plan if step["action"] == "repair"]
    assert repairs[0]["preconditions_met"] is True
