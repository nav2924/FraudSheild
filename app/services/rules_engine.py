import os, yaml
from types import SimpleNamespace

RULES_PATH = os.getenv("RULES_PATH", "config/rules.yml")

def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _to_ns(x):
    if isinstance(x, dict):
        # recursively convert dicts to namespaces for dot-access
        return SimpleNamespace(**{k: _to_ns(v) for k, v in x.items()})
    return x

def eval_expr(expr: str, features: dict) -> bool:
    """
    Evaluate a small expression like:
      "not features.device_seen_before and features.amount_inr >= 75000"
    with dot-access allowed on 'features'.
    """
    fns = _to_ns(features or {})
    try:
        # provide both dot-access ('features') and original dict ('f') if someone writes features["..."]
        return bool(eval(expr, {"__builtins__": {}}, {"features": fns, "f": features}))
    except Exception as e:
        print(f"[rules] eval error for '{expr}': {e}")
        return False

def apply_rules(features: dict, rules: dict):
    reasons = []
    risk = 0.0

    for r in rules.get("hard_stops", []):
        if eval_expr(r["if"], features):
            return 1.0, [r["id"]], r.get("action", "HOLD")

    for s in rules.get("soft_signals", []):
        if eval_expr(s["if"], features):
            reasons.append(s["id"])
            risk += float(s.get("weight", 0.1))

    risk = max(0.0, min(1.0, risk))
    return risk, reasons, None
    