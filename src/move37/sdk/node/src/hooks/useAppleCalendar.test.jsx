// @vitest-environment jsdom

import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useAppleCalendar } from "./useAppleCalendar";

function createJsonResponse(body) {
  return {
    ok: true,
    status: 200,
    text: async () => JSON.stringify(body),
  };
}

describe("useAppleCalendar", () => {
  it("loads status and events for the requested range", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        createJsonResponse({
          enabled: true,
          connected: true,
          provider: "apple",
          writableCalendarId: "calendar://primary",
          calendars: [{ id: "calendar://primary", name: "primary", readOnly: false }],
        }),
      )
      .mockResolvedValueOnce(
        createJsonResponse({
          events: [
            {
              id: "event-1",
              calendarId: "calendar://primary",
              calendarName: "primary",
              title: "Deep work",
              startsAt: "2026-03-17T00:00:00+00:00",
              endsAt: "2026-03-18T00:00:00+00:00",
              allDay: true,
              linkedActivityId: "wake-early",
              managedByMove37: true,
            },
          ],
        }),
      );

    const { result } = renderHook(() =>
      useAppleCalendar({
        baseUrl: "",
        token: "token",
        fetchImpl,
        range: {
          start: "2026-03-17T00:00:00Z",
          end: "2026-03-24T00:00:00Z",
        },
      }),
    );

    await waitFor(() => expect(result.current.status).not.toBeNull());
    expect(result.current.events).toHaveLength(1);
    expect(result.current.events[0].linkedActivityId).toBe("wake-early");
  });
});
