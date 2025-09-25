# 🚀 FraudShield 360  

**AI-Powered UEBA + Tamper-Proof Blockchain Logging, streamed with Kafka, containerized with Docker**  

---

## 📌 TL;DR (30-sec pitch, non-tech)  
Today’s fraud tools are **noisy** (false alarms), **rigid** (rules can’t keep up), and **opaque** (no clear reasons).  

**FraudShield 360** learns each customer’s **normal behaviour**, flags unusual actions, **explains why**, and locks every decision on a **blockchain** so it can’t be secretly changed.  

⚡ Runs in real time with **Kafka** and deploys anywhere with **Docker**.  

---

## ❌ Cons of Existing Systems (Layman’s Terms)  
- 🚫 Too many false alarms → legit customers get blocked.  
- 🐌 Slow to adapt → fraudsters evolve faster than rules.  
- 👓 Tunnel vision → only looks at transactions (ignores devices/logins/peers).  
- ❓ No clear reasons → hard to justify to customers/regulators.  
- 📝 Logs can be edited → weak trust with auditors.  
- 📉 Legacy infra → can’t handle real-time spikes.  

---

## ✅ How FraudShield 360 Solves Them  
- **UEBA baselines** → learns per-user/entity → fewer false alarms.  
- **Anomaly models** → catch new fraud tricks without rules.  
- **Signal fusion** → transactions + logins + device + geo + peers.  
- **Explainability** → human reason codes + SHAP (optional).  
- **Blockchain ledger** → immutable audit (tamper-proof).  
- **Kafka streaming** → elastic, real-time ingestion/scoring.  
- **Docker** → one-click deploy local or cloud.  

---

## 🏗️ Architecture  

### Human Story (non-tech)  
1. We watch **all signals** (money movement, logins, devices, locations).  
2. We know your **normal habits**.  
3. If something looks unusual, the AI raises risk.  
4. We act smartly: allow / OTP selfie / hold / block.  
5. We explain **clearly why**.  
6. We write in **permanent ink** (blockchain).  
7. We learn from feedback every week.  

---

## 🔄 End-to-End Flow  
1. **Customer Action** → Kafka event.  
2. **Feature Enrichment** → UEBA + Rules.  
3. **Scoring** → Risk + Reasons.  
4. **Decision** → Allow / Challenge / Block.  
5. **Immutable Record** → Blockchain.  
6. **Analyst Feedback** → Retraining.  

**Sample Event JSON**  
```json
{
  "event_id": "e_924f",
  "user_id": "U18273",
  "channel": "netbanking",
  "action": "transfer",
  "amount_inr": 90000,
  "device_id_hash": "d9c1…",
  "ip": "49.205.x.y",
  "geo": {"lat": 9.98, "lon": 76.28},
  "ts": "2025-09-19T10:05:22+05:30"
}
```
---
## Scoring Response JSON
```
{
  "risk": 0.87,
  "action": "HOLD",
  "reasons": [
    "amount 10x user median",
    "first-time device",
    "login time outside usual window"
  ],
  "model_version": "iforest_v3.2",
  "rules_triggered": ["new_device_high_amount"],
  "ts": "2025-09-19T10:05:23+05:30"
}
```
---

## 🛠️Tech Stack
-Ingestion/Streaming → Apache Kafka (Redpanda works too).
-API/Scoring → FastAPI/Flask + Gunicorn/Uvicorn.
-ML → scikit-learn (IsolationForest), optional Autoencoder/Keras.
-Features & Baselines → Redis + Postgres.
-Blockchain/Notary → Local hash-chain JSON blocks (MVP) or Hyperledger Fabric (enterprise).
-Containers → Docker + docker-compose.
-UI → Flask/Jinja or React dashboard.
-Observability → Prometheus + Grafana.

---
## 📂 Folder Structure
```
fraudshield360/
├── docker-compose.yml
├── requirements.txt
├── run.sh                  # starts everything together
├── app/
│   ├── routes/        # api.py, dashboard.py
│   ├── services/      # kafka_consumer, feature_engineering, scorer, blockchain_logger
│   ├── templates/     # dashboard.html
│   └── static/        # app.css
├── config/            # rules.yml, kafka.yml
├── data/              # sample_events.jsonl
├── models/            # iforest_v1.pkl
└── scripts/           # seed_kafka.py, retrain_offline.py
```
---

## 🐳 Quick Start
```
# Make run.sh executable
chmod +x run.sh  

# Run everything (Kafka + API + Worker + Dashboard)
./run.sh  

# Seed demo events
docker exec -it fraudshield360-api-1 python scripts/seed_kafka.py
```
---

## 📊 Rules Policy (YAML snippet)
```
hard_stops:
  - id: new_device_high_amount
    if: "not features.device_seen_before and features.amount_inr > 75000"
    action: "HOLD"

soft_signals:
  - id: night_owl
    weight: 0.2
    if: "features.hour in [0,1,2,3,4]"

thresholds:
  allow_below: 0.35
  stepup_between: [0.35, 0.7]
  block_above: 0.7
```

---

## 📈 Success Metrics

-🔒 Tamper check: Always OK across N decisions.
-🎯 Alert Precision ↑ (30% fewer false positives).
-📊 TPR ↑ (same or better detection than rules).
-💡 Explainability: ≥3 reasons per decision.
-⚡ Latency: <100ms per scoring call.

---

