// src/api/policy.api.js

import api from "./client";

export const getPolicy = async () => {
  const res = await api.get("/policy/");
  return res.data;
};

export const updatePolicy = async (payload) => {
  const res = await api.patch("/policy/", payload);
  return res.data;
};