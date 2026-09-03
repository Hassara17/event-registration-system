import api from "./axios";

export const assignStaffToSession = async (sessionId, staffId) => {
  const response = await api.post(
    `/sessions/${sessionId}/staff/${staffId}`
  );

  return response.data;
};

export const removeStaffFromSession = async (sessionId, staffId) => {
  const response = await api.delete(
    `/sessions/${sessionId}/staff/${staffId}`
  );

  return response.data;
};

export const getSessionStaff = async (sessionId) => {
  const response = await api.get(
    `/sessions/${sessionId}/staff`
  );

  return response.data;
};

export const getMyAssignedSessions = async () => {
  const response = await api.get(
    "/sessions/my/assigned"
  );

  return response.data;
};