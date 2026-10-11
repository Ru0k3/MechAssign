# Knowledge Representation & Forward Chaining

**Code:** `backend/knowledge/rules.py`, `backend/knowledge/inference.py`, `backend/knowledge/questions.py`

## 1. The AI concept

A **rule-based (production) system** represents knowledge as a set of `IF <condition> THEN <conclusion>` rules operating over a shared pool of facts ("working memory"). Reasoning proceeds by **inference**, and the two classic strategies are:

- **Forward chaining** (data-driven): start from known facts, fire any rule whose condition they satisfy, add the rule's conclusions back into the fact pool as *new* facts, and repeat until no more rules fire. This is how expert systems (e.g. MYCIN) diagnose from symptoms toward a conclusion.
- **Backward chaining** (goal-driven): start from a hypothesis/goal and work backward, asking "what facts would let some rule prove this?" — used by Prolog-style systems.

This project uses **forward chaining**: known symptoms flow forward into derived conclusions (specialist needed, parts needed, urgency).

## 2. The knowledge base (`rules.py`)

```python
DAMAGE_TYPES = ["engine", "brakes", "window/glass", "tires", "exhaust", "internal parts", "electronics"]

RULES = [
    {"when": {"damage_type": "engine"},        "then": {"specialist_needed": "engine",        "parts_needed": True, "urgency": 5}},
    {"when": {"damage_type": "brakes"},        "then": {"specialist_needed": "brakes",        "parts_needed": True, "urgency": 5}},
    ...
]
```

This is a flat list of **production rules**, each a pure-data `{when: ..., then: ...}` dict — deliberately not hard-coded `if/elif` chains, so the knowledge ("what implies what") is separated from the inference engine (the code that applies it). That separation — rules as data, inference as a generic engine over that data — is the defining trait of a knowledge-based system, and is the thing to point at if asked "where's the knowledge representation?"

Each rule's `when` clause matches one `damage_type`, and its `then` clause asserts three derived facts: which specialist is needed, whether a part is needed, and a base urgency score (1–10 scale; glass/exhaust/electronics are lower urgency, engine/brakes are highest at 5).

`backend/knowledge/questions.py` holds one **clarifying question per damage type** (e.g. *"Does the brake pedal feel soft or sink?"*) — this is the knowledge engineer's way of eliciting exactly the one extra fact the inference engine needs to refine its conclusion, mirroring how an expert system interviews a user for symptoms rather than demanding every fact up front.

## 3. The inference engine (`inference.py`)

```python
def infer_facts(damage_type, answers, has_part):
    facts = {"damage_type": damage_type, "answers": answers, "has_part": has_part}
    derived = {}

    # Step 1: base rule — fires directly off damage_type
    for rule in RULES:
        if rule["when"]["damage_type"] == damage_type:
            for key in rule["then"]:
                derived[key] = rule["then"][key]

    # Step 2: fires off the DERIVED facts + the answer — the actual chaining step.
    answer_text = answers.get(damage_type, "").lower()
    severe_words = ["yes", "severe", "shattered", "loud"]

    if derived.get("urgency") and any(word in answer_text for word in severe_words):
        derived["urgency"] = min(derived["urgency"] + 3, 10)

    if has_part:
        derived["parts_needed"] = False

    return derived
```

This is a **two-step forward chain**, and the two steps matter for different reasons:

1. **Step 1 — base rule firing.** The raw input fact `damage_type` is matched against `RULES`, and its `then` clause's facts (`specialist_needed`, `parts_needed`, `urgency`) are asserted into `derived`. This alone is just a lookup table — it only becomes *chaining* once step 2 reuses `derived`'s output as step 2's input.
2. **Step 2 — derived-fact-dependent rule.** The severity bump only fires by checking `derived.get("urgency")` — a fact produced by step 1 — combined with the raw follow-up answer. This is forward chaining's defining feature: a later rule consumes an *earlier rule's conclusion*, not just the original input. If a technician told you "we just check `if answer == 'yes': urgency += 3`" without going through `derived`, that would *not* be forward chaining — it would just be a nested conditional. The chain here is one hop deep (base fact → derived fact → final fact), but the mechanism generalizes to arbitrarily many hops if more rules referenced `derived` fields.
3. **The `has_part` override** is a third, independent fact-override step: if the driver already has the replacement part, `parts_needed` is forced to `False` regardless of what the damage-type rule said — overriding a derived fact with a more specific observation, another common pattern in rule-based systems (specificity ordering / defeasible rules).

**Implementation detail worth knowing:** the `facts` dict (holding `damage_type`, `answers`, `has_part`) is built at the top of the function but is **never returned** — only `derived` is. It reads as an intended "working memory" object that the final implementation didn't end up needing, since `derived` alone has everything `app.py` consumes. If asked in Q&A, this is a correct observation about the code, not a bug that breaks anything (the dict is simply dead).

**Severity-word matching is a substring/keyword check**, not real NLP (`severe_words = ["yes", "severe", "shattered", "loud"]`, checked via `in`) — it's a deliberately simple stand-in so the follow-up answer (free text or a yes/no dropdown in the UI) can still trip the escalation rule without needing any language understanding. This keeps the whole system in the "classical, explainable logic" category rather than pulling in anything statistical.

## 4. What flows out

`infer_facts()` returns a dict like:

```python
{"specialist_needed": "engine", "parts_needed": True, "urgency": 8}
```

which `run_pipeline()` (`backend/app.py:79`) immediately hands to the **CSP allocator** (`specialist_needed` becomes the specialty constraint, see `03-csp.md`) and to the **adversarial comparison** (`urgency` becomes the MAX player's payoff, see `06-adversarial-search.md`). This is the pipeline's first stage precisely because every later stage depends on facts it derives.

## 5. Presentation talking points

- Rules are **data**, not code — the inference engine (`infer_facts`) is generic and would handle new rules added to `RULES` without modification. This is the textbook separation of *knowledge* from *inference* in a knowledge-based system.
- It's forward chaining because conclusions feed forward into further conclusions (`derived["urgency"]` is both written and read within the same chain), not because "it starts from the top of a list."
- The chain here is shallow (2 hops) by design — enough to demonstrate the mechanism without needing a fixed-point loop (`while facts changed: fire all matching rules` ), which a textbook/production expert system would use for arbitrarily long chains.
