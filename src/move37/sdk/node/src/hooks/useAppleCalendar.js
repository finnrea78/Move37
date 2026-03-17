import { useEffect, useMemo, useState } from "react";

import { Move37Client } from "../client";

export function useAppleCalendar(options) {
  const headersKey = JSON.stringify(options.defaultHeaders ?? {});
  const client = useMemo(
    () =>
      new Move37Client({
        baseUrl: options.baseUrl,
        token: options.token,
        defaultHeaders: options.defaultHeaders,
        fetchImpl: options.fetchImpl,
      }),
    [options.baseUrl, options.fetchImpl, options.token, headersKey],
  );
  const [status, setStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reconciling, setReconciling] = useState(false);
  const [error, setError] = useState(null);

  async function reload(range = null) {
    setLoading(true);
    setError(null);
    try {
      const nextStatus = await client.getAppleCalendarStatus();
      setStatus(nextStatus);
      if (!range?.start || !range?.end) {
        setEvents([]);
        return { status: nextStatus, events: [] };
      }
      const nextEvents = await client.listAppleCalendarEvents(range);
      setEvents(nextEvents.events || []);
      return { status: nextStatus, events: nextEvents.events || [] };
    } catch (nextError) {
      const wrapped = nextError instanceof Error ? nextError : new Error(String(nextError));
      setError(wrapped);
      throw wrapped;
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!options.range?.start || !options.range?.end) {
      void reload(null);
      return;
    }
    void reload(options.range);
  }, [client, options.range?.end, options.range?.start]);

  async function reconcile(range = options.range) {
    setReconciling(true);
    setError(null);
    try {
      const result = await client.reconcileAppleCalendar();
      await reload(range ?? null);
      return result;
    } catch (nextError) {
      const wrapped = nextError instanceof Error ? nextError : new Error(String(nextError));
      setError(wrapped);
      throw wrapped;
    } finally {
      setReconciling(false);
    }
  }

  return {
    status,
    events,
    loading,
    reconciling,
    error,
    reload,
    reconcile,
  };
}
