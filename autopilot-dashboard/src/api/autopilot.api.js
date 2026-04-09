// src/api/autopilot.api.js

import api from "./client";

export const getAutopilotStatus = async () => {
  const res = await api.get("/autopilot/status/");
  return res.data;
};

export const updateAutopilotMode = async (cloud_account_id, mode) => {
  const res = await api.post("/autopilot/mode/", {
    cloud_account_id,
    mode
  });
  return res.data;
};

export const runAutopilotNow = async () => {
  const res = await api.post("/autopilot/run/");
  return res.data;
};
