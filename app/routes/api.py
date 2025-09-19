import os, json, time
from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.services.blockchain_logger import log_decision

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_SCORED = os.getenv("TOPIC_SCORED", "events.scored")

app = FastAPI(title=os.getenv("APP_NAME", "FraudShield360"))

# ---- Lazy/Retrying Kafka producer ----
_producer = None
_last_fail_ts = 0
_backoff_sec = 3

def get_producer():
    """
    Create a KafkaProducer lazily with simple backoff so the API can boot
    even if Kafka is not yet available.
    """
    global _producer, _last_fail_ts
    if _producer is not None:
        return _producer
    # basic cooldown to avoid hammering on failure
    now = time.time()
    if now - _last_fail_ts < _backoff_sec:
        return None
    try:
        from kafka import KafkaProducer
        _producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            linger_ms=10,
        )
        return _producer
    except Exception as e:
        _last_fail_ts = now
        # don't crash app startup — just run without producer for now
        print(f"[api] Kafka producer not ready: {e}")
        return None
# --------------------------------------

class Event(BaseModel):
    event_id: str
    user_id: str
    channel: str
    action: str
    amount_inr: float = Field(0)
    device_id_hash: str | None = None
    ip: str | None = None
    geo: dict | None = None
    ts: str

@app.get("/health")
def health():
    # health is OK if API is up; Kafka may still be coming up
    ready = get_producer() is not None
    return {"status": "ok", "service": "api", "kafka_producer_ready": ready}

@app.post("/score")
def score(evt: Event):
    # Placeholder scoring (Step 1)
    risk = 0.12
    action = "ALLOW"
    reasons = ["baseline not trained (demo stub)"]

    response = {
        "event_id": evt.event_id,
        "risk": risk,
        "action": action,
        "reasons": reasons,
        "model_version": "stub_v0",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
    }

    # Try to publish scored event; if Kafka not yet ready, skip silently
    prod = get_producer()
    if prod:
        try:
            prod.send(TOPIC_SCORED, response)
        except Exception as e:
            print(f"[api] send to Kafka failed: {e}")

    # Always write to local ledger
    log_decision({
        "event_id": evt.event_id,
        "risk": risk,
        "action": action,
        "reasons": reasons,
        "model_version": "stub_v0",
        "ts": response["ts"],
    })

    return response
