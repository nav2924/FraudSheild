export default function Badge({ action }) {
  const color =
    action === "ALLOW" ? "bg-green-50 text-green-700 border-green-200"
  : action === "HOLD"  ? "bg-amber-50 text-amber-700 border-amber-200"
  : action === "BLOCK" ? "bg-red-50 text-red-700 border-red-200"
  : "bg-gray-100 text-gray-700 border-gray-200"
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${color}`}>
      {action || "—"}
    </span>
  )
}
