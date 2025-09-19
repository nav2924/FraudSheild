from typing import Dict, Any
from .baselines import get_user_stats, device_seen_before, peer_stats

def enrich_features(evt: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal parse
    ts = evt.get("ts", "")
    hour = int(ts[11:13]) if len(ts) >= 13 else None
    amt = float(evt.get("amount_inr", 0) or 0)
    uid = evt.get("user_id")
    dev = evt.get("device_id_hash")

    ustats = get_user_stats(uid)
    dev_seen = device_seen_before(uid, dev)

    # peer z-score (robust)
    med, rstd = peer_stats()
    peer_z = (amt - med) / rstd if rstd else 0.0

    # simple session velocity hook (placeholder)
    # could track last event ts per user in Redis; omitted for Step 2 simplicity

    return {
        "event_id": evt.get("event_id"),
        "user_id": uid,
        "channel": evt.get("channel"),
        "action": evt.get("action"),
        "amount_inr": amt,
        "hour": hour,
        "user_median": ustats["median"],
        "user_p90": ustats["p90"],
        "device_seen_before": dev_seen,
        "peer_z": peer_z,
    }
