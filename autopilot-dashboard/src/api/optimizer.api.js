import api from "./client";

export async function getOptimizer() {
  const res = await api.get("/optimizer/");
  return res.data;
}

export async function applyOptimization(id) {
  const res = await api.post("/optimizer/apply/", { id });
  return res.data;
}