import json, random, argparse
from datetime import datetime, timedelta

IST_OFFSET = "+05:30"

def ist_iso(dt: datetime) -> str:
    # format: YYYY-MM-DDTHH:MM:SS+05:30
    return dt.strftime(f"%Y-%m-%dT%H:%M:%S{IST_OFFSET}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/sample_events.jsonl")
    ap.add_argument("--users", type=int, default=50)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)
    now = datetime(2025, 9, 19, 10, 0, 0)  # anchor similar to your examples
    start = now - timedelta(days=args.days)

    rows = []
    for u in range(1, args.users + 1):
        user_id = f"U{1000 + u}"
        # per-user baseline spend ~ ₹1k–₹8k
        base_amt = random.randint(1000, 8000)
        # primary device & occasional new devices
        primary_dev = f"d{user_id[-2:]}A"
        known_devs = {primary_dev}
        # sessions per user
        n_events = random.randint(30, 80)

        t = start + timedelta(minutes=random.randint(0, 60))
        for i in range(n_events):
            # progress time
            t += timedelta(minutes=random.randint(10, 360))

            # choose action (mostly transfers + some add_payee, login)
            action = random.choices(
                ["transfer", "transfer", "transfer", "add_payee", "login"],
                weights=[40, 30, 20, 6, 4],
                k=1
            )[0]

            channel = random.choice(["netbanking", "mobile", "atm", "card"])
            dev_choice = primary_dev if random.random() < 0.9 else f"d{user_id[-2:]}{random.choice('BCDE')}"
            if dev_choice != primary_dev:
                known_devs.add(dev_choice)

            geo = {"lat": round(8.0 + random.random()*10, 2),
                   "lon": round(72.0 + random.random()*10, 2)}

            amount = 0
            if action == "transfer":
                # normal transfers: jitter around base_amt
                amount = max(0, int(random.gauss(base_amt, max(400, 0.15*base_amt))))

                # occasional very small or zero-amount test
                if random.random() < 0.05:
                    amount = random.randint(1, 200)

                # inject anomalies (≈2–3%)
                if random.random() < 0.025:
                    # 10x–20x spike, new device, night hours (0–4)
                    amount = base_amt * random.randint(10, 20)
                    dev_choice = f"dNEW{random.randint(1,999)}"
                    hour = random.randint(0, 4)
                    t = t.replace(hour=hour, minute=random.randint(0, 59), second=0, microsecond=0)

            # compose event row
            evt = {
                "event_id": f"e_{user_id}_{i}",
                "user_id": user_id,
                "channel": channel,
                "action": action,
                "amount_inr": amount,
                "device_id_hash": dev_choice,
                "ip": f"10.0.{random.randint(0,255)}.{random.randint(1,254)}",
                "geo": geo,
                "ts": ist_iso(t),
            }
            rows.append(evt)

    # add your original 3 events for continuity
    rows.extend([
        {"event_id":"e_1","user_id":"U1001","channel":"netbanking","action":"transfer","amount_inr":5000,"device_id_hash":"dA","ip":"10.0.0.1","geo":{"lat":9.98,"lon":76.28},"ts":"2025-09-19T10:00:00+05:30"},
        {"event_id":"e_2","user_id":"U1001","channel":"netbanking","action":"add_payee","amount_inr":0,"device_id_hash":"dA","ip":"10.0.0.1","geo":{"lat":9.98,"lon":76.28},"ts":"2025-09-19T10:02:00+05:30"},
        {"event_id":"e_3","user_id":"U1001","channel":"netbanking","action":"transfer","amount_inr":90000,"device_id_hash":"dB","ip":"49.205.x.y","geo":{"lat":9.98,"lon":76.28},"ts":"2025-09-19T02:03:00+05:30"},
    ])

    # write JSONL
    with open(args.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[gen] wrote {len(rows)} events to {args.out}")

if __name__ == "__main__":
    main()
