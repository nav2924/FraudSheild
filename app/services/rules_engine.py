import os, yaml

RULES_PATH = os.getenv("RULES_PATH", "config/rules.yml")

def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def eval_expr(expr: str, features: dict) -> bool:
    # Safe-ish eval context
    allowed = {"features": features}
    return bool(eval(expr, {"__builtins__": {}}, allowed))  # expressions are controlled by us

def apply_rules(features: dict, rules: dict):
    reasons = []
    risk = 0.0

    # hard stops
    for r in rules.get("hard_stops", []):
        if eval_expr(r["if"], features):
            return 1.0, [r["id"]], r.get("action", "HOLD")  # immediate hold/block

    # soft signals → additive risk
    for s in rules.get("soft_signals", []):
        if eval_expr(s["if"], features):
            reasons.append(s["id"])
            risk += float(s.get("weight", 0.1))

    # cap risk in [0, 1]
    risk = max(0.0, min(1.0, risk))
    return risk, reasons, None
