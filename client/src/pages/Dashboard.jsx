import { useState, useMemo } from "react"
import { API } from "../services/api"
import { usePolling } from "../hooks/usePolling"
import Layout from "../components/Layout"
import Toolbar from "../components/Toolbar"
import DataTable from "../components/DataTable"
import Flash from "../components/Flash"

export default function Dashboard() {
  const [rows, setRows] = useState([])
  const [decisions, setDecisions] = useState(0)
  const [verifyText, setVerifyText] = useState("")
  const [query, setQuery] = useState("")
  const [actionFilter, setActionFilter] = useState("ALL")
  const [sortKey, setSortKey] = useState("ts_desc")
  const [flash, setFlash] = useState("")
  const [pauseMs, setPauseMs] = useState(0)   // to temporarily pause polling after actions
  const [savingId, setSavingId] = useState(null) // row-level saving state

  const load = async () => {
    const s = await API.getStats()
    setDecisions(s.decisions ?? 0)
    const d = await API.getDecisions(200)
    setRows(d)
  }

  usePolling(load, 2000, pauseMs) // slight change: hook supports a pause delay

  const onVerify = async () => {
    setVerifyText("Verifying…")
    try {
      const v = await API.verify()
      setVerifyText(v.ok ? `OK (count ${v.count})` : `TAMPERED (count ${v.count})`)
      setFlash("Chain verified")
    } catch {
      setVerifyText("Verify failed")
      setFlash("Verify failed")
    }
  }

  const onLabel = async (decision_id, event_id, label) => {
    try {
      setSavingId(decision_id)
      // optimistic UI: reflect label immediately
      setRows(prev => prev.map(r => r.decision_id === decision_id ? { ...r, label } : r))
      // pause polling briefly to avoid a refetch during the click handler window
      setPauseMs(1200)
      await API.label({ decision_id, event_id, label })
      setFlash(`Saved: ${label}`)
    } catch {
      // roll back label if needed (optional)
      setFlash("Label failed")
    } finally {
      setSavingId(null)
      // allow polling again
      setTimeout(() => setPauseMs(0), 300)
    }
  }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    const list = rows.filter(r =>
      (!q || (r.event_id || "").toLowerCase().includes(q) || (r.decision_id || "").toLowerCase().includes(q)) &&
      (actionFilter === "ALL" || r.action === actionFilter)
    )
    return list.sort((a, b) => {
      if (sortKey === "ts_desc") return String(b.ts||"").localeCompare(String(a.ts||""))
      if (sortKey === "ts_asc")  return String(a.ts||"").localeCompare(String(b.ts||""))
      if (sortKey === "risk_desc") return (b.risk ?? -1) - (a.risk ?? -1)
      if (sortKey === "risk_asc")  return (a.risk ??  1) - (b.risk ??  1)
      return 0
    })
  }, [rows, query, actionFilter, sortKey])

  return (
    <Layout>
      <Toolbar
        decisions={decisions}
        verifyText={verifyText}
        onVerify={onVerify}
        query={query}
        setQuery={setQuery}
        actionFilter={actionFilter}
        setActionFilter={setActionFilter}
        sortKey={sortKey}
        setSortKey={setSortKey}
      />
      <DataTable rows={filtered} onLabel={onLabel} savingId={savingId} />
      <Flash message={flash} onDone={() => setFlash("")} />
    </Layout>
  )
}
