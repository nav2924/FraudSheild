import { useEffect, useRef } from "react"

/**
 * Simple interval-based polling.
 * returns a stop function (optional: you can ignore it if not needed).
 */
export function usePolling(fn, ms) {
  const ref = useRef(null)
  useEffect(() => {
    fn() // kick once
    ref.current = setInterval(fn, ms)
    return () => clearInterval(ref.current)
  }, [ms]) // fn is stable enough for our case
}
