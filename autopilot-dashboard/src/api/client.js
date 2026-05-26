// src/api/client.js

import axios from "axios";

// Production API URL
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "https://api.autopilotops.cloud/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach token + organization
api.interceptors.request.use(
  (config) => {

    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    const org = JSON.parse(
      localStorage.getItem("active_org")
    );

    if (org?.id) {
      config.headers["X-Organization-ID"] = org.id;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Auto refresh token
api.interceptors.response.use(
  (response) => response,

  async (error) => {

    const originalRequest = error.config;

    // Prevent infinite retry loop
    if (
      error.response?.status === 401 &&
      !originalRequest._retry
    ) {

      originalRequest._retry = true;

      try {

        const refresh =
          localStorage.getItem("refresh");

        if (!refresh) {
          throw new Error("No refresh token");
        }

        const res = await axios.post(
          "https://api.autopilotops.cloud/api/v1/token/refresh/",
          {
            refresh,
          }
        );

        const newAccess = res.data.access;

        // Save new token
        localStorage.setItem(
          "token",
          newAccess
        );

        // Retry original request
        originalRequest.headers.Authorization =
          `Bearer ${newAccess}`;

        return api(originalRequest);

      } catch (refreshError) {

        console.error(
          "Token refresh failed:",
          refreshError
        );

        // Logout user
        localStorage.removeItem("token");
        localStorage.removeItem("refresh");
        localStorage.removeItem("active_org");

        window.location.href = "/login";

        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;