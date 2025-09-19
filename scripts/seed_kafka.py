import os, json, time
from kafka import KafkaProducer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_RAW = os.getenv("TOPIC_RAW", "events.raw")
PATH = "data/sample_events.jsonl"

def main():
    prod = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=10,
    )
    sent = 0
    with open(PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            prod.send(TOPIC_RAW, json.loads(line))
            sent += 1
    prod.flush()
    print(f"[seed] published {sent} events to {TOPIC_RAW}")

if __name__ == "__main__":
    main()
