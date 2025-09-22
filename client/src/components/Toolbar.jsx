export default function Toolbar({
  decisions,
  verifyText,
  onVerify,
  query,
  setQuery,
  actionFilter,
  setActionFilter,
  sortKey,
  setSortKey,
}) {
  return (
    <div className="space-y-3">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <h1 className="text-2xl font-bold">FraudShield 360 — Analyst</h1>
        <div className="ml-0 sm:ml-2 px-3 py-1 rounded-lg bg-gray-50 border text-sm">
          Decisions: <b>{decisions}</b>
        </div>
        <button onClick={onVerify} className="px-3 py-1 rounded-lg border hover:bg-gray-50">
          Verify Chain
        </button>
        <span className="text-gray-500">{verifyText}</span>
        <div className="sm:ml-auto text-gray-500">Auto-refresh: <b>2s</b></div>
      </header>

      <div className="flex flex-wrap gap-2 items-center">
        <input
          value={query}
          onChange={(e)=>setQuery(e.target.value)}
          placeholder="Search event_id / decision_id…"
          className="border rounded-lg px-3 py-1.5"
        />
        <select value={actionFilter} onChange={(e)=>setActionFilter(e.target.value)} className="border rounded-lg px-3 py-1.5">
          <option value="ALL">All actions</option>
          <option value="ALLOW">ALLOW</option>
          <option value="HOLD">HOLD</option>
          <option value="BLOCK">BLOCK</option>
        </select>
        <select value={sortKey} onChange={(e)=>setSortKey(e.target.value)} className="border rounded-lg px-3 py-1.5">
          <option value="ts_desc">Newest first</option>
          <option value="ts_asc">Oldest first</option>
          <option value="risk_desc">Risk high→low</option>
          <option value="risk_asc">Risk low→high</option>
        </select>
      </div>
    </div>
  )
}
