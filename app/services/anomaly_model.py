import os, json, joblib, numpy as np, random
from typing import Dict, Tuple, List, Iterable
from sklearn.ensemble import IsolationForest

MODELS_DIR  = os.getenv("MODELS_DIR", "models")
MODEL_PATH  = os.path.join(MODELS_DIR, "iforest_v1.pkl")
DATA_PATH   = os.getenv("SYNTH_EVENTS_PATH", "data/sample_events.jsonl")
SEED        = int(os.getenv("FS360_SEED", "42"))

MODEL_FEATURES = [
    "amount_inr", "hour", "user_median", "user_p90", "peer_z", "device_seen_before",
]

def features_to_vector(features: Dict) -> np.ndarray:
    return np.array([
        float(features.get("amount_inr", 0) or 0.0),
        float((features.get("hour") if features.get("hour") is not None else -1)),
        float(features.get("user_median", 0) or 0.0),
        float(features.get("user_p90", 0) or 0.0),
        float(features.get("peer_z", 0) or 0.0),
        float(1.0 if features.get("device_seen_before") else 0.0),
    ], dtype=np.float32)

def _batch_to_matrix(rows: List[Dict]) -> np.ndarray:
    return np.vstack([features_to_vector(f) for f in rows]) if rows else np.empty((0, len(MODEL_FEATURES)), dtype=np.float32)

def load_model(path: str = MODEL_PATH) -> Tuple[object, str]:
    if not os.path.exists(path):
        return None, "rules_only"
    model = joblib.load(path)
    return model, os.path.basename(path).replace(".pkl", "")

def anomaly_score(model, features: Dict) -> float:
    if model is None:
        return 0.0
    raw = model.score_samples(features_to_vector(features).reshape(1, -1))[0]
    a, b = -4.0, 0.0
    return float(1.0 / (1.0 + np.exp(-(a * raw + b))))

# ---- JSONL trainer (no Redis needed) ----
def _iter_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if line:
                try: yield json.loads(line)
                except: pass

def _approx_user_stats(events: List[Dict]) -> None:
    from statistics import median
    by_user = {}
    for e in events:
        if e.get("action")=="transfer" and (e.get("amount_inr") or 0)>0:
            by_user.setdefault(e["user_id"], []).append(float(e["amount_inr"]))
    u_stats = {u:(median(v), v[max(0,int(0.9*(len(v)-1)))]) for u,v in ((u,sorted(v)) for u,v in by_user.items())}
    seen = {}
    for e in events:
        u=e.get("user_id"); d=e.get("device_id_hash")
        if u not in seen: seen[u]=set()
        e["_device_seen_before"]= d in seen[u]
        if d: seen[u].add(d)
        med,p90 = u_stats.get(u, (0.0,0.0))
        e["_user_median"]=med; e["_user_p90"]=p90
    amts=[float(e.get("amount_inr") or 0) for e in events if e.get("action")=="transfer" and (e.get("amount_inr") or 0)>0]
    if amts:
        med = median(amts); mad = median([abs(x-med) for x in amts]) or 1.0; rstd = 1.4826*mad
        for e in events:
            amt=float(e.get("amount_inr") or 0); e["_peer_z"]=(amt-med)/rstd if rstd else 0.0
    else:
        for e in events: e["_peer_z"]=0.0

def _inline_enrich(e: Dict) -> Dict:
    ts=e.get("ts",""); hour=int(ts[11:13]) if len(ts)>=13 else None
    return {
        "amount_inr": float(e.get("amount_inr",0) or 0),
        "hour": hour,
        "_hour": hour,  # handy for debugging
        "user_median": float(e.get("_user_median",0) or 0),
        "user_p90": float(e.get("_user_p90",0) or 0),
        "peer_z": float(e.get("_peer_z",0) or 0),
        "device_seen_before": bool(e.get("_device_seen_before", False)),
    }

def train_from_synthetic_jsonl(
    jsonl_path: str = DATA_PATH,
    out_path: str = MODEL_PATH,
    contamination: float = 0.05,
    n_estimators: int = 200,
    random_seed: int = SEED,
) -> str:
    random.seed(random_seed); np.random.seed(random_seed)
    events = [e for e in _iter_jsonl(jsonl_path) if e.get("action")=="transfer" and (e.get("amount_inr") or 0)>0]
    if not events: raise RuntimeError(f"No training transfers in {jsonl_path}")
    _approx_user_stats(events)
    feats = [_inline_enrich(e) for e in events]
    X = _batch_to_matrix(feats)
    if X.shape[0] < 10: raise RuntimeError(f"Too few rows to train: {X.shape[0]}")
    model = IsolationForest(n_estimators=n_estimators, max_samples="auto",
                            contamination=contamination, random_state=random_seed,
                            bootstrap=False, n_jobs=-1).fit(X)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(model, out_path)
    print(f"[retrain] wrote {out_path}, n={len(X)}")
    return out_path
