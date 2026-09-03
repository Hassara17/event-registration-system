import { useState, useEffect, useCallback } from 'react';
import { capacityAlertService } from '../services/capacityAlertService';

export const useCapacityAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await capacityAlertService.getAlerts();
      setAlerts(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch capacity alerts');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const dismiss = async (alertId) => {
    try {
      await capacityAlertService.dismissAlert(alertId);
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to dismiss alert');
    }
  };

  return { alerts, loading, error, dismiss, refetch: fetchAlerts };
};