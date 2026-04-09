import { useEffect, useState } from "react";
import {
  getMembers,
  addMember,
  inviteMember,
  removeMember,
  updateRole,
  getInvites,
  cancelInvite,
  resendInvite,
} from "../../api/team.api";

export default function Team() {
  const [members, setMembers] = useState([]);
  const [invites, setInvites] = useState([]);

  const [email, setEmail] = useState("");
  const [role, setRole] = useState("VIEWER");
  const [loading, setLoading] = useState(false);

  // -----------------------------
  // LOAD DATA
  // -----------------------------
  async function loadMembers() {
    try {
      const res = await getMembers();
      setMembers(res);
    } catch (err) {
      console.error("Failed to load members", err);
    }
  }

  async function loadInvites() {
    try {
      const res = await getInvites();
      setInvites(res);
    } catch (err) {
      console.error("Failed to load invites", err);
    }
  }

  useEffect(() => {
    loadMembers();
    loadInvites();
  }, []);

  // -----------------------------
  // ACTIONS
  // -----------------------------
  async function handleAdd() {
    if (!email) return alert("Email required");

    setLoading(true);
    try {
      await addMember({ email, role });
      setEmail("");
      await loadMembers();
    } catch (err) {
      alert(err.response?.data?.error || "Failed to add member");
    }
    setLoading(false);
  }

  async function handleInvite() {
    if (!email) return alert("Email required");

    setLoading(true);
    try {
      await inviteMember({ email, role });
      alert("Invitation sent");
      setEmail("");
      await loadInvites();
    } catch (err) {
      alert(err.response?.data?.error || "Failed to invite");
    }
    setLoading(false);
  }

  async function handleRemove(email) {
    if (!confirm("Remove this member?")) return;

    try {
      await removeMember({ email });
      await loadMembers();
    } catch (err) {
      alert(err.response?.data?.error || "Failed to remove member");
    }
  }

  async function handleRoleChange(email, newRole) {
    try {
      await updateRole({ email, role: newRole });
      await loadMembers();
    } catch (err) {
      alert(err.response?.data?.error || "Failed to update role");
    }
  }

  async function handleCancel(email) {
    if (!confirm("Cancel this invite?")) return;

    try {
      await cancelInvite({ email });
      await loadInvites();
    } catch (err) {
      alert(err.response?.data?.error || "Failed to cancel invite");
    }
  }

  async function handleResend(email) {
    try {
      await resendInvite({ email });
      alert("Invite resent successfully");
    } catch (err) {
      alert(err.response?.data?.error || "Failed to resend invite");
    }
  }

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="space-y-6">

      {/* ============================= */}
      {/* ADD / INVITE */}
      {/* ============================= */}
      <div className="bg-panel border border-border rounded-lg p-6">
        <h2 className="font-semibold mb-4">Add or Invite Member</h2>

        <div className="flex gap-3">
          <input
            className="input flex-1"
            placeholder="Email address"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />

          <select
            className="input"
            value={role}
            onChange={e => setRole(e.target.value)}
          >
            <option value="VIEWER">Viewer</option>
            <option value="ADMIN">Admin</option>
          </select>

          <button
            onClick={handleAdd}
            className="bg-primary px-4 rounded text-white"
            disabled={loading}
          >
            Add
          </button>

          <button
            onClick={handleInvite}
            className="bg-border px-4 rounded"
            disabled={loading}
          >
            Invite
          </button>
        </div>
      </div>

      {/* ============================= */}
      {/* PENDING INVITES */}
      {/* ============================= */}
      <div className="bg-panel border border-border rounded-lg p-6">
        <h2 className="font-semibold mb-4">Pending Invites</h2>

        {invites.length === 0 ? (
          <p className="text-sm text-muted">No pending invites</p>
        ) : (
          invites.map((i, idx) => (
            <div
              key={idx}
              className="flex justify-between items-center py-3 border-t border-border"
            >
              <div>
                <div className="font-medium">{i.email}</div>
                <div className="text-xs text-muted">
                  Expires: {new Date(i.expires_at).toLocaleDateString()}
                </div>
              </div>

              <div className="flex items-center gap-3">

                {/* ROLE BADGE */}
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    i.role === "ADMIN"
                      ? "bg-blue-500 text-white"
                      : "bg-gray-500 text-white"
                  }`}
                >
                  {i.role}
                </span>

                {/* ACTIONS */}
                <button
                  onClick={() => handleResend(i.email)}
                  className="text-blue-500 text-xs hover:underline"
                >
                  Resend
                </button>

                <button
                  onClick={() => handleCancel(i.email)}
                  className="text-red-500 text-xs hover:underline"
                >
                  Cancel
                </button>

              </div>
            </div>
          ))
        )}
      </div>

      {/* ============================= */}
      {/* MEMBERS LIST */}
      {/* ============================= */}
      <div className="bg-panel border border-border rounded-lg p-6">
        <h2 className="font-semibold mb-4">Team Members</h2>

        <table className="w-full text-sm">
          <thead className="text-muted">
            <tr>
              <th className="text-left py-2">Email</th>
              <th className="text-left">Role</th>
              <th className="text-left">Joined</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {members.map((m, i) => (
              <tr key={i} className="border-t border-border">
                <td className="py-2">{m.email}</td>

                {/* ROLE */}
                <td>
                  {m.role === "OWNER" ? (
                    <span className="px-2 py-1 rounded text-xs bg-yellow-500 text-black">
                      OWNER
                    </span>
                  ) : (
                    <select
                      value={m.role}
                      onChange={e =>
                        handleRoleChange(m.email, e.target.value)
                      }
                      className="bg-transparent border border-border rounded px-2 py-1 text-xs"
                    >
                      <option value="ADMIN">Admin</option>
                      <option value="VIEWER">Viewer</option>
                    </select>
                  )}
                </td>

                {/* JOINED */}
                <td>
                  {new Date(m.joined_at).toLocaleDateString()}
                </td>

                {/* REMOVE */}
                <td className="text-right">
                  {m.role !== "OWNER" && (
                    <button
                      onClick={() => handleRemove(m.email)}
                      className="text-red-500 hover:underline"
                    >
                      Remove
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

      </div>

    </div>
  );
}