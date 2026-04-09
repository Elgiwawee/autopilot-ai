import api from "./client";

export const getMembers = async () => {
  const res = await api.get("/members/");
  return res.data;
};

export const addMember = async (data) => {
  return api.post("/members/add/", data);
};

export const inviteMember = async (data) => {
  return api.post("/invite/", data);
};

export const removeMember = async (data) => {
  return api.delete("/members/remove/", { data });
};

export const updateRole = async (data) => {
  return api.patch("/members/role/", data);
};

export const acceptInvite = (token) => {
  return api.post(`/invite/accept/${token}/`);
};

export const getInvites = async () => {
  const res = await api.get("/invites/");
  return res.data;
};

export const cancelInvite = data =>
  api.delete("/invite/cancel/", { data });

export const resendInvite = data =>
  api.post("/invite/resend/", data);