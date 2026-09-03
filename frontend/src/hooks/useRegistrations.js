import { useCallback, useEffect, useState } from "react";
import registrationService from "../services/registrationService";

export const useRegistrations = () => {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchRegistrations = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const data =
        await registrationService.getMyRegistrations();

      setRegistrations(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      console.error(
        "Failed to load registrations:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Unable to load registrations."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRegistrations();
  }, [fetchRegistrations]);

  return {
    registrations,
    loading,
    error,
    fetchRegistrations,
  };
};

export default useRegistrations;