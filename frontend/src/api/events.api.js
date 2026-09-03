import api from "./axios";


// Get events
export const getEvents = async (params = {}) => {
  const response = await api.get("/events", {
    params,
  });

  return response.data;
};


// Get single event
export const getEvent = async (eventId) => {
  const response = await api.get(`/events/${eventId}`);

  return response.data;
};


// Create event
export const createEvent = async (eventData) => {
  const response = await api.post("/events", eventData);

  return response.data;
};


// Update event
export const updateEvent = async (eventId, eventData) => {
  const response = await api.patch(
    `/events/${eventId}`,
    eventData
  );

  return response.data;
};


// Archive event
export const archiveEvent = async (eventId) => {
  const response = await api.post(
    `/events/${eventId}/archive`
  );

  return response.data;
};


// Restore event
export const restoreEvent = async (eventId) => {
  const response = await api.post(
    `/events/${eventId}/restore`
  );

  return response.data;
};


// Delete event
export const deleteEvent = async (eventId) => {
  const response = await api.delete(
    `/events/${eventId}`
  );

  return response.data;
};