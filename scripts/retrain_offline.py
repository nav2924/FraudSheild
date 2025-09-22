import os, json, random
from app.services.feature_engineering import enrich_features
from app.services.baselines import update_user_baselines
from app.services.anomaly_model import MODELS_DIR
from sklearn.ensemble import IsolationForest
import joblib, numpy as np

DATA_PATH = "data/sample_events.jsonl"
OUT_PATH  = os.path.join(os.getenv("MODELS_DIR", MODELS_DIR), "iforest_v1.pkl")

def load_events(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def main():
    events = list(load_events(DATA_PATH))
    if not events:
        raise SystemExit(f"No events at {DATA_PATH}")

    # 1) Warm baselines (simulate historical flow)
    for e in events:
        amt = float(e.get("amount_inr") or 0)
        update_user_baselines(e.get("user_id"), amt, e.get("device_id_hash"))

    # 2) Build features (focus on transfers with amount)
    feats = []
    for e in events:
        if e.get("action") == "transfer" and (e.get("amount_inr") or 0) > 0:
            feats.append(enrich_features(e))

    X = []
    for f in feats:
        # inline mapping identical to wrapper to avoid circular import
        vec = [
            float(f.get("amount_inr", 0) or 0.0),
            float((f.get("hour") if f.get("hour") is not None else -1)),
            float(f.get("user_median", 0) or 0.0),
            float(f.get("user_p90", 0) or 0.0),
            float(f.get("peer_z", 0) or 0.0),
            float(1.0 if f.get("device_seen_before") else 0.0),
        ]
        X.append(vec)
    X = np.array(X, dtype=np.float32)

    model = IsolationForest(
        n_estimators=200,
        max_samples="auto",
        contamination=0.05,
        random_state=42,
        bootstrap=False,
        n_jobs=-1,
    ).fit(X)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    joblib.dump(model, OUT_PATH)
    print(f"[retrain] wrote {OUT_PATH}, n={len(X)}")

if __name__ == "__main__":
    main()
