import { useState, useMemo } from "react"
import { API } from "../services/api"
import { usePolling } from "../hooks/usePolling"
import Layout from "../components/Layout"
import Toolbar from "../components/Toolbar"
import DataTable from "../components/DataTable"

export default function Dashboard() {
  const [rows, setRows] = useState([])
  const [decisions, setDecisions] = useState(0)
  const [verifyText, setVerifyText] = useState("")
  const [query, setQuery] = useState("")
  const [actionFilter, setActionFilter] = useState("ALL")
  const [sortKey, setSortKey] = useState("ts_desc")

  const load = async () => {
    try {
      const s = await API.getStats()
      setDecisions(s.decisions ?? 0)
      const d = await API.getDecisions(200)
      setRows(d)
    } catch (e) {
      // optional: toast or console
      // console.error(e)
    }
  }

  usePolling(load, 2000)

  const onVerify = async () => {
    setVerifyText("Verifying…")
    try {
      const v = await API.verify()
      setVerifyText(v.ok ? `OK (count ${v.count})` : `TAMPERED (count ${v.count})`)
    } catch (e) {
      setVerifyText("Verify failed")
    }
  }

  const onLabel = async (decision_id, event_id, label) => {
    try {
      await API.label({ decision_id, event_id, label })
      alert(`Saved label: ${label}`)
    } catch (e) {
      alert("Label failed: " + e.message)
    }
  }

  // client-side filter + sort
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
      <DataTable rows={filtered} onLabel={onLabel} />
    </Layout>
  )
}
