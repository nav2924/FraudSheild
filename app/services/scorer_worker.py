import os, json, time
from kafka import KafkaConsumer, KafkaProducer, errors
from app.services.rules_engine import load_rules, apply_rules
from app.services.decisioning import decide
from app.services.blockchain_logger import log_decision

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_FEATURES = os.getenv("TOPIC_FEATURES", "events.features")
TOPIC_SCORED   = os.getenv("TOPIC_SCORED", "events.scored")
TOPIC_CASES    = os.getenv("TOPIC_CASES", "cases")

_consumer = _producer = None

def get_consumer():
    global _consumer
    if _consumer: return _consumer
    while True:
        try:
            _consumer = KafkaConsumer(
                TOPIC_FEATURES,
                bootstrap_servers=BOOTSTRAP,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="fs360-scorers",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            print("[scorer] connected to kafka")
            return _consumer
        except errors.NoBrokersAvailable:
            print("[scorer] kafka not ready, retrying in 2s...")
            time.sleep(2)

def get_producer():
    global _producer
    if _producer: return _producer
    while True:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                linger_ms=50,
            )
            print("[scorer] producer ready")
            return _producer
        except errors.NoBrokersAvailable:
            print("[scorer] kafka not ready for producer, retrying in 2s...")
            time.sleep(2)

def main():
    rules = load_rules()
    consumer = get_consumer()
    producer = get_producer()
    print("[scorer] started")
    for msg in consumer:
        features = (msg.value or {}).get("features", {})
        risk, reason_ids, hard_action = apply_rules(features, rules)
        action, reasons = decide(risk, reason_ids, hard_action)
        resp = {
            "event_id": features.get("event_id"),
            "user_id": features.get("user_id"),
            "risk": round(risk, 3),
            "action": action,
            "reasons": reasons,
            "model_version": "rules_v1",
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
        }
        producer.send(TOPIC_SCORED, resp)
        if action in ("STEP_UP", "HOLD"):
            producer.send(TOPIC_CASES, {"event_id": resp["event_id"], "action": action, "reasons": reasons, "ts": resp["ts"]})
        log_decision({
            "event_id": resp["event_id"], "risk": resp["risk"], "action": resp["action"],
            "reasons": resp["reasons"], "model_version": resp["model_version"], "ts": resp["ts"],
        })
        print("[scorer] decision→", resp["event_id"], resp["action"], resp["risk"], resp["reasons"])

if __name__ == "__main__":
    main()
