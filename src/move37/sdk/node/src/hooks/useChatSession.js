import { useMemo, useState } from "react";

import { Move37Client } from "../client";

export function useChatSession(options) {
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
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function createSession(payload = {}) {
    setLoading(true);
    setError(null);
    try {
      const next = await client.createChatSession(payload);
      setSession(next);
      return next;
    } catch (nextError) {
      const wrapped = nextError instanceof Error ? nextError : new Error(String(nextError));
      setError(wrapped);
      throw wrapped;
    } finally {
      setLoading(false);
    }
  }

  async function reload(sessionId) {
    setLoading(true);
    setError(null);
    try {
      const next = await client.getChatSession(sessionId);
      setSession(next);
      return next;
    } catch (nextError) {
      const wrapped = nextError instanceof Error ? nextError : new Error(String(nextError));
      setError(wrapped);
      throw wrapped;
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage(sessionId, payload) {
    setLoading(true);
    setError(null);
    try {
      const result = await client.sendChatMessage(sessionId, payload);
      setSession((current) =>
        current
          ? {
              ...current,
              messages: [...current.messages, result.userMessage, result.assistantMessage],
              lastMessageAt: result.assistantMessage.createdAt,
            }
          : current,
      );
      return result;
    } catch (nextError) {
      const wrapped = nextError instanceof Error ? nextError : new Error(String(nextError));
      setError(wrapped);
      throw wrapped;
    } finally {
      setLoading(false);
    }
  }

  return {
    session,
    loading,
    error,
    createSession,
    reload,
    sendMessage,
  };
}
