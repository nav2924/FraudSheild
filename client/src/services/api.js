// Centralized API helpers and endpoints
export async function fetchJSON(url, opts) {
  const r = await fetch(url, opts)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export const API = {
  getStats: () => fetchJSON("/stats"),
  verify:   () => fetchJSON("/verify"),
  getDecisions: (limit = 200) => fetchJSON(`/decisions?limit=${limit}`),
  label: (payload) => fetchJSON("/label", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }),
}

// POST analyst label to backend
export async function postLabel({ decision_id, event_id, label }) {
  const res = await fetch("/label", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision_id, event_id, label }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// GET blockchain verify
export async function verifyChain() {
  const res = await fetch("/verify");
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
