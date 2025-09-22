# app/routes/dashboard.py
from flask import Flask, jsonify, request
import os, json, sqlite3
from datetime import datetime

app = Flask(__name__)

# --- Config / paths ----------------------------------------------------------
LEDGER_JSONL = os.environ.get("LEDGER_JSONL", "data/ledger.jsonl")
LEDGER_SQLITE = os.environ.get("LEDGER_SQLITE", "data/ledger.db")
# Table name for sqlite chain (adjust if your blockchain_logger uses another):
SQLITE_TABLE = os.environ.get("LEDGER_TABLE", "chain")

def parse_block_row(block):
    """
    Normalize a ledger block (JSON dict) into a UI-friendly decision row.
    Expected block shape:
      {
        "decision_id": "d_657a",
        "prev_hash": "...",
        "payload_sha256": "...",
        "payload": {
          "event_id": "e_924f",
          "risk": 0.87,
          "action": "HOLD",
          "reasons": ["amount 10x", "new device", "odd hour"],
          "model_version": "iforest_v3.2",
          "ts": "2025-09-19T10:05:23+05:30"
        },
        "block_ts": "2025-09-19T10:05:24+05:30"
      }
    """
    p = block.get("payload", {}) or {}
    # Prefer payload.ts, else block_ts
    ts = p.get("ts") or block.get("block_ts") or ""
    return {
        "decision_id": block.get("decision_id") or "",
        "event_id": p.get("event_id") or "",
        "risk": p.get("risk"),
        "action": p.get("action") or "",
        "reasons": p.get("reasons") or [],
        "model_version": p.get("model_version") or "",
        "ts": ts
    }

# --- Data access: JSONL or SQLite -------------------------------------------
def ledger_exists():
    if os.path.isfile(LEDGER_JSONL):
        return "jsonl"
    if os.path.isfile(LEDGER_SQLITE):
        return "sqlite"
    return None

def read_blocks_jsonl(limit=200, offset=0):
    rows = []
    if not os.path.isfile(LEDGER_JSONL):
        return rows
    # Read tail-efficiently
    with open(LEDGER_JSONL, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Latest first
    for line in reversed(lines[offset:]):
        line = line.strip()
        if not line:
            continue
        try:
            block = json.loads(line)
            rows.append(parse_block_row(block))
            if len(rows) >= limit:
                break
        except Exception:
            continue
    return rows

def read_blocks_sqlite(limit=200, offset=0):
    rows = []
    if not os.path.isfile(LEDGER_SQLITE):
        return rows
    conn = sqlite3.connect(LEDGER_SQLITE)
    try:
        cur = conn.cursor()
        # Assumes a table with columns: decision_id TEXT, payload TEXT, block_ts TEXT, prev_hash TEXT, payload_sha256 TEXT
        # Adjust if your schema differs.
        cur.execute(
            f"""
            SELECT decision_id, payload, block_ts
            FROM {SQLITE_TABLE}
            ORDER BY datetime(block_ts) DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        for decision_id, payload_json, block_ts in cur.fetchall():
            try:
                payload = json.loads(payload_json) if payload_json else {}
            except Exception:
                payload = {}
            block = {
                "decision_id": decision_id,
                "payload": payload,
                "block_ts": block_ts,
            }
            rows.append(parse_block_row(block))
    finally:
        conn.close()
    return rows

def count_blocks_jsonl():
    if not os.path.isfile(LEDGER_JSONL):
        return 0
    with open(LEDGER_JSONL, "r", encoding="utf-8") as f:
        return sum(1 for _ in f if _.strip())

def count_blocks_sqlite():
    if not os.path.isfile(LEDGER_SQLITE):
        return 0
    conn = sqlite3.connect(LEDGER_SQLITE)
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(1) FROM {SQLITE_TABLE}")
        (n,) = cur.fetchone()
        return int(n or 0)
    finally:
        conn.close()

# --- Routes used by the React UI --------------------------------------------
@app.get("/decisions")
def decisions():
    """Return recent decisions for the UI table."""
    limit = int(request.args.get("limit", 200))
    offset = int(request.args.get("offset", 0))
    source = ledger_exists()
    if source == "jsonl":
        rows = read_blocks_jsonl(limit=limit, offset=offset)
    elif source == "sqlite":
        rows = read_blocks_sqlite(limit=limit, offset=offset)
    else:
        return jsonify({"error": "ledger not found", "paths_checked": [LEDGER_JSONL, LEDGER_SQLITE]}), 404
    return jsonify(rows)

@app.get("/stats")
def stats():
    """Return simple stats for header counter."""
    source = ledger_exists()
    if source == "jsonl":
        n = count_blocks_jsonl()
    elif source == "sqlite":
        n = count_blocks_sqlite()
    else:
        n = 0
    return jsonify({"decisions": n})

@app.post("/label")
def label():
    """
    Save analyst feedback (simple append-only JSONL at data/labels.jsonl).
    Expect JSON: { "decision_id": "...", "event_id": "...", "label": "fraud" | "not_fraud" }
    """
    payload = request.get_json(force=True, silent=True) or {}
    decision_id = payload.get("decision_id", "")
    event_id = payload.get("event_id", "")
    label = payload.get("label", "")
    if label not in ("fraud", "not_fraud"):
        return jsonify({"ok": False, "error": "label must be 'fraud' or 'not_fraud'"}), 400

    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "labels.jsonl")
    rec = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "decision_id": decision_id,
        "event_id": event_id,
        "label": label,
    }
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return jsonify({"ok": True})
