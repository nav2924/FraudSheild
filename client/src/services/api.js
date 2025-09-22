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
