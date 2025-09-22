import json, os, time
from kafka import KafkaProducer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_RAW = os.getenv("TOPIC_RAW", "events.raw")

def main():
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    with open("data/sample_events.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            evt = json.loads(line)
            producer.send(TOPIC_RAW, evt)
            print("sent→", evt["event_id"])
            time.sleep(0.05)  # throttle for demo
    producer.flush()

if __name__ == "__main__":
    main()
