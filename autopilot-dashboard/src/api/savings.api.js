// src/api/savings.js

import api from "./client";

export const getSavingsOverview = async () => {
  const res = await api.get("/savings/overview");
  return res.data;
};

export const getSavingsTrend = async () => {
  const res = await api.get("/savings/trend");
  return res.data;
};

export const getRecommendations = async () => {
  const res = await api.get("/savings/recommendations");
  return res.data;
};

export const exportSavingsCSV = () =>
  api.get("/savings/export/csv/", { responseType: "blob" });