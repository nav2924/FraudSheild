import { useEffect, useRef } from "react"

export function usePolling(fn, ms = 2000, pauseMs = 0) {
  const timer = useRef(null);
  useEffect(() => {
    let canceled = false;

    const loop = async () => {
      try {
        await fn();
      } catch {}
      if (canceled) return;
      const wait = pauseMs > 0 ? pauseMs : ms;
      timer.current = setTimeout(loop, wait);
    };

    loop();
    return () => {
      canceled = true;
      if (timer.current) clearTimeout(timer.current);
    };
  }, [fn, ms, pauseMs]);
}
