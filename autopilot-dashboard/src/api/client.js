// src/api/client.js

import axios from "axios";

const api = axios.create({
  baseURL: "http://13.62.55.71:8000/api/v1",
  headers: {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
  },

});


// Attach token + organization
api.interceptors.request.use((config) => {

  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const org = JSON.parse(localStorage.getItem("active_org"));

  if (org?.id) {
    config.headers["X-Organization-ID"] = org.id;
  }

  return config;
});


// Auto refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {

    const originalRequest = error.config;

    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {

      originalRequest._retry = true;

      try {

        const refresh = localStorage.getItem("refresh");

        const res = await axios.post(
          "http://13.62.55.71:8000/api/token/refresh/",
          { refresh }
        );

        const newAccess = res.data.access;

        localStorage.setItem("token", newAccess);

        // update header
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;

        return api(originalRequest);

      } catch (refreshError) {

        // refresh failed → logout
        localStorage.removeItem("token");
        localStorage.removeItem("refresh");

        window.location.href = "/login";

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;