// src/api/cloudAccounts.js

import api from "./client";

export const fetchCloudAccounts = async () => {
  const res = await api.get("/cloud-accounts/");
  return res.data.results;   
};

export const createCloudAccount = async (data) => {
  const res = await api.post("/cloud-accounts/", data);
  return res.data;
};

export const disableCloudAccount = async (id) => {
  await api.delete(`/cloud-accounts/${id}`);
};