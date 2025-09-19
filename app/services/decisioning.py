import os

ALLOW_BELOW = float(os.getenv("ALLOW_BELOW", 0.35))
STEPUP_LOW  = float(os.getenv("STEPUP_LOW", 0.35))
STEPUP_HIGH = float(os.getenv("STEPUP_HIGH", 0.7))
BLOCK_ABOVE = float(os.getenv("BLOCK_ABOVE", 0.7))

def decide(risk: float, reasons: list[str], hard_action: str | None = None):
    if hard_action:
        return hard_action, reasons
    if risk < ALLOW_BELOW:
        return "ALLOW", reasons
    if STEPUP_LOW <= risk < STEPUP_HIGH:
        return "STEP_UP", reasons
    if risk >= BLOCK_ABOVE:
        return "HOLD", reasons
    # fallback
    return "ALLOW", reasons
