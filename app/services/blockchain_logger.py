import os, json, time, hashlib, uuid
from typing import Dict, Optional

LEDGER_PATH = os.getenv("LEDGER_PATH", "data/ledger.jsonl")

def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _read_last_hash(path: str) -> Optional[str]:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return None
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell()
        # read last line efficiently
        buf = bytearray()
        while pos:
            pos -= 1
            f.seek(pos)
            ch = f.read(1)
            if ch == b"\n" and buf:
                break
            buf.extend(ch)
        line = bytes(reversed(buf)).decode("utf-8").strip()
    try:
        rec = json.loads(line)
        return rec.get("hash")
    except Exception:
        return None

def log_decision(payload: Dict) -> Dict:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    prev_hash = _read_last_hash(LEDGER_PATH) or "GENESIS"
    decision_id = f"d_{uuid.uuid4().hex[:6]}"
    block_ts = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())
    inner = {
        "decision_id": decision_id,
        "prev_hash": prev_hash,
        "payload": payload,
        "block_ts": block_ts,
    }
    payload_sha256 = _sha256_hex(json.dumps(payload, sort_keys=True))
    inner["payload_sha256"] = payload_sha256
    block_hash = _sha256_hex(prev_hash + payload_sha256 + decision_id + block_ts)
    record = {"hash": block_hash, **inner}
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record

def verify_chain(path: str = None) -> Dict:
    path = path or LEDGER_PATH
    if not os.path.exists(path):
        return {"ok": True, "count": 0}
    prev_hash = "GENESIS"
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            expected = _sha256_hex(
                prev_hash + rec["payload_sha256"] + rec["decision_id"] + rec["block_ts"]
            )
            if expected != rec["hash"]:
                return {"ok": False, "at_index": count, "message": "TAMPERED"}
            prev_hash = rec["hash"]
            count += 1
    return {"ok": True, "count": count}
