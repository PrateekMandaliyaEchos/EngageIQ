import { useEffect, useRef } from 'react';

interface UsePollingOptions {
  interval: number;
  enabled?: boolean;
}

export const usePolling = (
  callback: () => void,
  options: UsePollingOptions
) => {
  const { interval, enabled = true } = options;
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Execute callback immediately
    callback();

    // Set up polling
    intervalRef.current = setInterval(callback, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [callback, interval, enabled]);

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  return { stopPolling };
};

