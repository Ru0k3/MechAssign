QUESTIONS = {
    "engine": "Does the engine make a loud knocking sound?",
    "brakes": "Does the brake pedal feel soft or sink?",
    "window/glass": "Is the glass shattered or only cracked?",
    "tires": "Is the tire fully flat?",
    "exhaust": "Is there loud noise or visible smoke?",
    "internal parts": "Is the vehicle leaking fluid inside the cabin?",
    "electronics": "Does the car fail to start or only lose accessories?"
}


def get_question(damage_type):
    """Return the follow-up question for the selected component."""
    return QUESTIONS.get(damage_type, "Can you describe the symptom?")
