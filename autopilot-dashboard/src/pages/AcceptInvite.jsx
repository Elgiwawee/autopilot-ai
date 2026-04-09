// src/pages/AcceptInvite.jsx

import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { acceptInvite } from "../api/team.api";
import { useAuth } from "../context/AuthContext";

export default function AcceptInvite() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, loading } = useAuth();

  const [status, setStatus] = useState("idle"); 
  // idle | loading | success | error

  useEffect(() => {
    async function processInvite() {
      if (loading) return;

      // ❌ Not logged in → redirect to login
      if (!isAuthenticated) {
        navigate(`/login?next=/invite/${token}`);
        return;
      }

      // ✅ Accept invite
      setStatus("loading");
      try {
        await acceptInvite(token);
        setStatus("success");

        setTimeout(() => {
          navigate("/overview");
        }, 1500);

      } catch (err) {
        setStatus("error");
      }
    }

    processInvite();
  }, [isAuthenticated, loading]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">

      <div className="bg-panel border border-border rounded-lg p-8 w-96 text-center space-y-4">

        {/* LOGO */}
        <img
          src="/logo.png"
          alt="Autopilot"
          className="h-12 mx-auto mb-4"
        />

        <h1 className="text-xl font-semibold">
          Join Organization
        </h1>

        {/* STATES */}
        {status === "loading" && (
          <p className="text-muted text-sm">
            Accepting invitation...
          </p>
        )}

        {status === "success" && (
          <p className="text-green-500 text-sm">
            ✅ Successfully joined! Redirecting...
          </p>
        )}

        {status === "error" && (
          <div className="space-y-3">
            <p className="text-red-500 text-sm">
              ❌ Invalid or expired invite
            </p>

            <button
              onClick={() => navigate("/overview")}
              className="bg-primary px-4 py-2 rounded text-white"
            >
              Go to Dashboard
            </button>
          </div>
        )}

        {/* IDLE (fallback button) */}
        {status === "idle" && isAuthenticated && (
          <button
            onClick={async () => {
              setStatus("loading");
              try {
                await acceptInvite(token);
                setStatus("success");
                setTimeout(() => navigate("/overview"), 1500);
              } catch {
                setStatus("error");
              }
            }}
            className="bg-primary px-6 py-2 rounded text-white"
          >
            Accept Invite
          </button>
        )}

      </div>
    </div>
  );
}