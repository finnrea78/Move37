export class ApiError extends Error {
  constructor(status, body, message) {
    super(message ?? `Move37 API request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export class Move37Client {
  constructor(options) {
    this.baseUrl = String(options.baseUrl ?? "").replace(/\/$/, "");
    this.token = options.token;
    this.defaultHeaders = options.defaultHeaders ?? {};
    this.fetchImpl =
      options.fetchImpl ??
      ((input, init) => globalThis.fetch(input, init));
  }

  setToken(token) {
    this.token = token;
  }

  authMe() {
    return this.request("GET", "/v1/auth/me");
  }

  getGraph() {
    return this.request("GET", "/v1/graph");
  }

  createActivity(payload) {
    return this.request("POST", "/v1/activities", { body: payload });
  }

  listNotes() {
    return this.request("GET", "/v1/notes");
  }

  getNote(noteId) {
    return this.request("GET", `/v1/notes/${encodeURIComponent(noteId)}`);
  }

  createNote(payload) {
    return this.request("POST", "/v1/notes", { body: payload });
  }

  updateNote(noteId, payload) {
    return this.request("PATCH", `/v1/notes/${encodeURIComponent(noteId)}`, { body: payload });
  }

  importTxtNotes(formData) {
    return this.requestMultipart("POST", "/v1/notes/import", formData);
  }

  searchNotes(payload) {
    return this.request("POST", "/v1/notes/search", { body: payload });
  }

  createChatSession(payload = {}) {
    return this.request("POST", "/v1/chat/sessions", { body: payload });
  }

  getChatSession(sessionId) {
    return this.request("GET", `/v1/chat/sessions/${encodeURIComponent(sessionId)}`);
  }

  sendChatMessage(sessionId, payload) {
    return this.request("POST", `/v1/chat/sessions/${encodeURIComponent(sessionId)}/messages`, {
      body: payload,
    });
  }

  insertBetween(activityId, payload) {
    return this.request("POST", `/v1/activities/${encodeURIComponent(activityId)}/insert-between`, {
      body: payload,
    });
  }

  updateActivity(activityId, payload) {
    return this.request("PATCH", `/v1/activities/${encodeURIComponent(activityId)}`, { body: payload });
  }

  startWork(activityId) {
    return this.request("POST", `/v1/activities/${encodeURIComponent(activityId)}/work/start`);
  }

  stopWork(activityId) {
    return this.request("POST", `/v1/activities/${encodeURIComponent(activityId)}/work/stop`);
  }

  forkActivity(activityId) {
    return this.request("POST", `/v1/activities/${encodeURIComponent(activityId)}/fork`);
  }

  deleteActivity(activityId, deleteTree = false) {
    return this.request("DELETE", `/v1/activities/${encodeURIComponent(activityId)}`, {
      query: { deleteTree },
    });
  }

  replaceDependencies(activityId, parentIds) {
    return this.request("PUT", `/v1/activities/${encodeURIComponent(activityId)}/dependencies`, {
      body: { parentIds },
    });
  }

  replaceSchedule(activityId, peers) {
    return this.request("PUT", `/v1/activities/${encodeURIComponent(activityId)}/schedule`, {
      body: { peers },
    });
  }

  deleteDependency(parentId, childId) {
    return this.request(
      "DELETE",
      `/v1/dependencies/${encodeURIComponent(parentId)}/${encodeURIComponent(childId)}`,
    );
  }

  deleteSchedule(earlierId, laterId) {
    return this.request(
      "DELETE",
      `/v1/schedules/${encodeURIComponent(earlierId)}/${encodeURIComponent(laterId)}`,
    );
  }

  async request(method, path, opts = {}) {
    const query = toQueryString(opts.query);
    const url = `${this.baseUrl}${path}${query ? `?${query}` : ""}`;
    const headers = {
      ...this.defaultHeaders,
    };

    if (opts.body !== undefined) {
      headers["Content-Type"] = "application/json";
    }
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await this.fetchImpl(url, {
      method,
      headers,
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined,
    });

    if (response.status === 204) {
      return null;
    }

    const text = await response.text();
    const parsed = parseBody(text);
    if (!response.ok) {
      throw new ApiError(response.status, parsed);
    }
    return parsed;
  }

  async requestMultipart(method, path, formData, opts = {}) {
    const query = toQueryString(opts.query);
    const url = `${this.baseUrl}${path}${query ? `?${query}` : ""}`;
    const headers = {
      ...this.defaultHeaders,
    };
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }
    const response = await this.fetchImpl(url, {
      method,
      headers,
      body: formData,
    });
    if (response.status === 204) {
      return null;
    }
    const text = await response.text();
    const parsed = parseBody(text);
    if (!response.ok) {
      throw new ApiError(response.status, parsed);
    }
    return parsed;
  }
}

function parseBody(value) {
  if (!value) {
    return null;
  }
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function toQueryString(input) {
  if (!input) {
    return "";
  }
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(input)) {
    if (value === undefined || value === null) {
      continue;
    }
    if (Array.isArray(value)) {
      value.forEach((entry) => params.append(key, String(entry)));
      continue;
    }
    params.append(key, String(value));
  }
  return params.toString();
}
