import os, json, statistics
from typing import Optional, Dict, Tuple
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_r = None
def r():
    global _r
    if _r is None:
        _r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _r

# Keys:
# fs:u:{user_id}:amts  -> JSON list of last N transfer amounts
# fs:u:{user_id}:dev   -> set of device hashes seen
# fs:peer:amts         -> JSON list of global peer amounts (coarse)

MAX_LIST = 200  # rolling history cap

def _json_get(key: str, default):
    val = r().get(key)
    if not val:
        return default
    try:
        return json.loads(val)
    except Exception:
        return default

def _json_set(key: str, obj):
    r().set(key, json.dumps(obj, ensure_ascii=False))

def update_user_baselines(user_id: str, amount_inr: float, device_id_hash: Optional[str]):
    # amounts
    k_amts = f"fs:u:{user_id}:amts"
    lst = _json_get(k_amts, [])
    if amount_inr and amount_inr > 0:
        lst.append(float(amount_inr))
        if len(lst) > MAX_LIST:
            lst = lst[-MAX_LIST:]
        _json_set(k_amts, lst)
        # also update peer/global distribution
        g = _json_get("fs:peer:amts", [])
        g.append(float(amount_inr))
        if len(g) > MAX_LIST * 20:
            g = g[-MAX_LIST*20:]
        _json_set("fs:peer:amts", g)

    # devices
    if device_id_hash:
        r().sadd(f"fs:u:{user_id}:dev", device_id_hash)

def get_user_stats(user_id: str) -> Dict:
    lst = _json_get(f"fs:u:{user_id}:amts", [])
    med = statistics.median(lst) if lst else 0.0
    p90 = statistics.quantiles(lst, n=10)[-1] if len(lst) >= 10 else med
    return {"count": len(lst), "median": med, "p90": p90}

def device_seen_before(user_id: str, device_id_hash: Optional[str]) -> bool:
    if not device_id_hash:
        return False
    return r().sismember(f"fs:u:{user_id}:dev", device_id_hash)

def peer_stats() -> Tuple[float, float]:
    g = _json_get("fs:peer:amts", [])
    if not g:
        return (0.0, 1.0)  # avoid zero division
    med = statistics.median(g)
    # robust dispersion (MAD ~ 1.4826 * median(|x - med|)), use as std proxy
    mad = statistics.median([abs(x - med) for x in g]) or 1.0
    robust_std = 1.4826 * mad
    return (med, robust_std)
