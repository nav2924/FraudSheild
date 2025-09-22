import Badge from "./Badge"
import Pill from "./Pill"
import { clamp2 } from "../utils/format"

export default function DataTable({ rows, onLabel }) {
  return (
    <div className="border rounded-2xl overflow-hidden">
      <div className="max-h-[75vh] overflow-auto">
        <table className="min-w-full text-sm">
          <thead className="sticky top-0 bg-gray-50 border-b">
            <tr>
              <th className="text-left p-2">Time</th>
              <th className="text-left p-2">Event</th>
              <th className="text-left p-2">Risk</th>
              <th className="text-left p-2">Action</th>
              <th className="text-left p-2">Reasons</th>
              <th className="text-left p-2">Model</th>
              <th className="text-left p-2">Label</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.decision_id} className="border-b hover:bg-gray-50">
                <td className="p-2">{r.ts || "—"}</td>
                <td className="p-2">
                  <div className="font-medium">{r.event_id}</div>
                  <div className="text-gray-500 text-xs">{r.decision_id}</div>
                </td>
                <td className="p-2">{clamp2(r.risk)}</td>
                <td className="p-2"><Badge action={r.action} /></td>
                <td className="p-2">{(r.reasons || []).map((x) => <Pill key={x} text={x} />)}</td>
                <td className="p-2">{r.model_version || "—"}</td>
                <td className="p-2 space-x-2">
                  <button
                    onClick={() => onLabel(r.decision_id, r.event_id, "fraud")}
                    className="px-2 py-1 rounded-md border hover:bg-gray-50"
                  >
                    Fraud
                  </button>
                  <button
                    onClick={() => onLabel(r.decision_id, r.event_id, "not_fraud")}
                    className="px-2 py-1 rounded-md border hover:bg-gray-50"
                  >
                    Not Fraud
                  </button>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr><td className="p-4 text-gray-500" colSpan={7}>No matching rows…</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
