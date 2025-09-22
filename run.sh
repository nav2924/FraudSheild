#!/usr/bin/env bash
set -euo pipefail

# Build all images (backend + frontend)
docker compose build

# Start everything
docker compose up -d

# Optional: train model from synthetic JSONL (if you want a fresh model each run)
# Comment out if you prefer to keep the existing model.
##!/usr/bin/env bash
set -euo pipefail

# Build all images (backend + frontend)
docker compose build

# Start everything
docker compose up -d

echo
echo "✅ All up!"
echo "UI:       http://localhost:5173"
echo "Backend:  http://localhost:8050/verify"
