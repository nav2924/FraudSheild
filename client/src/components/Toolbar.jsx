import { useState } from "react";
import { verifyChain } from "../services/api";

export default function Toolbar({ onAfterVerify }) {
  const [verifying, setVerifying] = useState(false);

  const onVerify = async () => {
    try {
      setVerifying(true);
      const res = await verifyChain();
      alert(`Blockchain: ${res.ok ? "OK" : "TAMPERED"} (blocks: ${res.count})`);
      onAfterVerify?.();
    } catch (e) {
      alert("Verify failed: " + e.message);
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className="flex items-center gap-2 mb-3">
      <button
        onClick={onVerify}
        disabled={verifying}
        className="px-3 py-1 rounded-md border hover:bg-gray-50 disabled:opacity-50"
      >
        {verifying ? "Verifying…" : "Verify Chain"}
      </button>
    </div>
  );
}
