import api from "./axios";


// ==========================================
// GET SESSION REGISTRATIONS
// ==========================================

export const getSessionRegistrations =
  async (sessionId) => {

    const response = await api.get(
      `/registrations/session/${sessionId}`
    );

    return response.data;
  };


// ==========================================
// GET SESSION STATS
// ==========================================

export const getSessionStats =
  async (sessionId) => {

    const response = await api.get(
      `/registrations/session/${sessionId}/stats`
    );

    return response.data;
  };


// ==========================================
// CONFIRM
// ==========================================

export const confirmRegistration =
  async (registrationId) => {

    const response = await api.post(
      `/registrations/${registrationId}/confirm`
    );

    return response.data;
  };


// ==========================================
// CHECK IN
// ==========================================

export const checkInRegistration =
  async (registrationId) => {

    const response = await api.post(
      `/registrations/${registrationId}/check-in`
    );

    return response.data;
  };


// ==========================================
// CANCEL
// ==========================================

export const cancelRegistration =
  async (registrationId) => {

    const response = await api.post(
      `/registrations/${registrationId}/cancel`
    );

    return response.data;
  };


// ==========================================
// CREATE REGISTRATION
// ==========================================

export const createRegistration =
  async (registrationData) => {

    const response = await api.post(
      "/registrations",
      registrationData
    );

    return response.data;
  };


// ==========================================
// GET MY REGISTRATIONS
// ==========================================

export const getMyRegistrations =
  async () => {

    const response = await api.get(
      "/registrations/my"
    );

    return response.data;
  };


// ==========================================
// GET REGISTRATION
// ==========================================

export const getRegistration =
  async (registrationId) => {

    const response = await api.get(
      `/registrations/${registrationId}`
    );

    return response.data;
  };


// ==========================================
// GET HISTORY
// ==========================================

export const getRegistrationHistory =
  async (registrationId) => {

    const response = await api.get(
      `/registrations/${registrationId}/history`
    );

    return response.data;
  };


// ==========================================
// SEARCH REGISTRATIONS
// ==========================================
export const searchRegistrations = async (params = {}) => {
  const response = await api.get("/registrations/search", {
    params: {
      search: params.search || undefined,
      event_id: params.event_id || undefined,
      session_id: params.session_id || undefined,
      registration_status:
        params.registration_status || undefined,

      page: params.page || 1,
      page_size: params.page_size || 10,

      sort_by: params.sort_by || "reserved_at",
      sort_order: params.sort_order || "desc",
    },
  });

  return response.data;
};



export const importRegistrationsCSV = async (sessionId, file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    `/registrations/session/${sessionId}/import`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export const exportSessionCheckin = async (sessionId) => {
  const response = await api.get(
    `/registrations/session/${sessionId}/export`,
    {
      responseType: "blob",
    }
  );

  return response;
};