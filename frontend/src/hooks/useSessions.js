import {
  useCallback,
  useEffect,
  useState,
} from "react";

import sessionService from "../services/sessionService";

function useSessions(eventId) {
  const [sessions, setSessions] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const loadSessions =
    useCallback(async () => {
      if (!eventId) {
        setSessions([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const data =
          await sessionService.getEventSessions(
            eventId
          );

        setSessions(data);
      } catch (error) {
        console.error(
          "Failed to load sessions:",
          error
        );

        setError(
          error.response?.data?.detail ||
          "Failed to load sessions."
        );
      } finally {
        setLoading(false);
      }
    }, [eventId]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return {
    sessions,
    loading,
    error,
    refresh: loadSessions,
  };
}

export default useSessions;

