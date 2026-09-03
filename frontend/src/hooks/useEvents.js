import { useCallback, useEffect, useState } from "react";

import eventService from "../services/eventService";

function useEvents(initialParams = {}) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [params, setParams] = useState({
    page: 1,
    page_size: 10,
    sort_by: "start_date",
    sort_order: "asc",
    ...initialParams,
  });

  const fetchEvents = useCallback(
    async (currentParams = params) => {
      try {
        setLoading(true);
        setError("");

        const data =
          await eventService.getEvents(
            currentParams
          );

        setEvents(data);
      } catch (error) {
        console.error(
          "Failed to load events:",
          error
        );

        setError(
          error.response?.data?.detail ||
          "Failed to load events."
        );
      } finally {
        setLoading(false);
      }
    },
    [params]
  );

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const updateParams = (newParams) => {
    setParams((previous) => ({
      ...previous,
      ...newParams,
    }));
  };

  const refresh = () => {
    fetchEvents();
  };

  return {
    events,
    loading,
    error,
    params,
    updateParams,
    refresh,
  };
}

export default useEvents;

