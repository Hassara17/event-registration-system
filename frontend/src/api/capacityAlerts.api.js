import api from "./axios";

export const getCapacityAlerts = async () => {
  const response = await api.get("/capacity-alerts");
  return response.data;
};

export const dismissCapacityAlert = async (sessionId) => {
  const response = await api.post(
    `/capacity-alerts/session/${sessionId}/dismiss`
  );

  return response.data;
};

