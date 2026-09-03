import api from "./axios";


// ======================================================
// GET SINGLE SESSION
// ======================================================

export const getSession = async (sessionId) => {
  const response = await api.get(
    `/sessions/${sessionId}`
  );

  return response.data;
};


// ======================================================
// GET ALL SESSIONS FOR EVENT
// ======================================================

export const getSessionsByEvent = async (eventId) => {
  const response = await api.get(
    `/sessions/event/${eventId}`
  );

  return response.data;
};


// ======================================================
// CREATE SESSION
// ======================================================

export const createSession = async (sessionData) => {
  const response = await api.post(
    "/sessions",
    null,
    {
      params: {
        event_id: sessionData.event_id,
        title: sessionData.title,
        start_time: sessionData.start_time,
        duration: sessionData.duration,
        location: sessionData.location,
        capacity: sessionData.capacity,
      },
    }
  );

  return response.data;
};


// ======================================================
// UPDATE SESSION
// ======================================================

export const updateSession = async (
  sessionId,
  sessionData
) => {
  const response = await api.patch(
    `/sessions/${sessionId}`,
    null,
    {
      params: {
        title: sessionData.title,
        start_time: sessionData.start_time,
        duration: sessionData.duration,
        location: sessionData.location,
        capacity: sessionData.capacity,
      },
    }
  );

  return response.data;
};


// ======================================================
// DELETE SESSION
// ======================================================

export const deleteSession = async (sessionId) => {
  const response = await api.delete(
    `/sessions/${sessionId}`
  );

  return response.data;
};