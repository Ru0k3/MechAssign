from backend.knowledge.rules import RULES


def infer_facts(damage_type, answers, has_part):
    facts = {"damage_type": damage_type, "answers": answers, "has_part": has_part}
    derived = {}

    # Step 1: base rule — fires directly off damage_type
    for rule in RULES:
        if rule["when"]["damage_type"] == damage_type:
            for key in rule["then"]:
                derived[key] = rule["then"][key]

    # Step 2: fires off the DERIVED facts + the answer — the actual chaining step.
    # Bumps urgency higher if the follow-up answer confirms something severe.
    answer_text = answers.get(damage_type, "").lower()
    severe_words = ["yes", "severe", "shattered", "loud"]

    if derived.get("urgency") and any(word in answer_text for word in severe_words):
        derived["urgency"] = min(derived["urgency"] + 3, 10)

    if has_part:
        derived["parts_needed"] = False

    return derived