import { useEffect } from "react";

export default function Flash({ message, kind = "info", onDone, ms = 1500 }) {
  useEffect(() => {
    if (!message) return;
    const t = setTimeout(() => onDone?.(), ms);
    return () => clearTimeout(t);
  }, [message, ms, onDone]);

  if (!message) return null;
  return (
    <div className={`fixed top-4 right-4 z-50 rounded-lg px-3 py-2 shadow
      ${kind === "error" ? "bg-red-600 text-white" : "bg-gray-900 text-white"}`}>
      {message}
    </div>
  );
}
