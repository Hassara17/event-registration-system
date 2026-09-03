import api from "./axios";

export const getCheckinStaff = async () => {
  const response = await api.get("/users/staff");

  return response.data;
};