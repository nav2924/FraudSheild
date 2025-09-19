import os, json, time
from kafka import KafkaConsumer, KafkaProducer, errors
from app.services.baselines import update_user_baselines
from app.services.feature_engineering import enrich_features

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_RAW = os.getenv("TOPIC_RAW", "events.raw")
TOPIC_FEATURES = os.getenv("TOPIC_FEATURES", "events.features")

_consumer = None
_producer = None

def get_consumer():
    global _consumer
    if _consumer:
        return _consumer
    while True:
        try:
            _consumer = KafkaConsumer(
                TOPIC_RAW,
                bootstrap_servers=BOOTSTRAP,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                group_id="fs360-consumers",
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            print("[worker] connected to kafka")
            return _consumer
        except errors.NoBrokersAvailable:
            print("[worker] kafka not ready, retrying in 2s...")
            time.sleep(2)

def get_producer():
    global _producer
    if _producer:
        return _producer
    while True:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                linger_ms=50,
            )
            print("[worker] producer ready")
            return _producer
        except errors.NoBrokersAvailable:
            print("[worker] kafka not ready for producer, retrying in 2s...")
            time.sleep(2)

def main():
    consumer = get_consumer()
    producer = get_producer()
    print("[worker] started: consuming", TOPIC_RAW)
    for msg in consumer:
        evt = msg.value
        update_user_baselines(evt.get("user_id"), float(evt.get("amount_inr") or 0), evt.get("device_id_hash"))
        features = enrich_features(evt)
        producer.send(TOPIC_FEATURES, {"features": features, "ts": time.time()})
        print("[worker] features→", features)

if __name__ == "__main__":
    main()
