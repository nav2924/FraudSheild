# FraudShield 360

AI-powered UEBA + tamper-proof blockchain logging, streamed with Kafka, containerized with Docker.

## Prerequisites
- Docker Desktop (or Docker Engine + Compose plugin)
- No local Kafka/Redis needed — they run in containers.

## First-time setup
Clone and go to repo root:
```bash
git clone <your-repo-url>.git
cd FraudSheild
```

## Start (daemon mode)
```bash
docker compose up -d --build
docker compose ps
```

## Health checks
- API: http://localhost:8000/health
- Dashboard (ledger verify UI): http://localhost:8050/

## Seed demo events
```bash
docker compose exec api python scripts/seed_kafka.py
```

## Follow Logs
```bash
# all containers
docker compose logs -f

# specific services
docker compose logs -f worker
docker compose logs -f scorer
docker compose logs -f kafka
docker compose logs -f api
```

## Stop(keep data/containers)
```bash
docker compose down
```

## Restart after changes
```bash
# Quick rebuild(uses cache):
docker compose up -d --build
# Clean rebuild(no cache):
docker compose build --no-cache
docker compose up -d
```

## Hard reset (stop + remove containers, networks, and named volumes if you added any)
```bash
docker compose down -v
```

## Useful one-liners
```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{"event_id":"e_demo","user_id":"U18273","channel":"netbanking","action":"transfer","amount_inr":90000,"device_id_hash":"NEW_DEV","ip":"49.205.x.y","geo":{"lat":9.98,"lon":76.28},"ts":"2025-09-19T02:03:00+05:30"}'

curl http://localhost:8050/verify
```