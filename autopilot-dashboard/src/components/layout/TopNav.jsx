// src/components/layout/TopNav.jsx

import { Globe, ChevronDown } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { useOrg } from "../../context/OrgContext";
import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ThemeToggle from "../ThemeToggle";

export default function TopNav() {
  const { user, logout } = useAuth();
  const { organization } = useOrg();

  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  // ✅ Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="h-14 border-b border-border bg-surface flex items-center justify-between px-6">

      {/* LEFT SIDE (LOGO) */}
      <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate("/overview")}>
        <img
          src="/logo.png"
          alt="Autopilot"
          className="h-12 object-contain"
        />
      </div>

      {/* RIGHT SIDE */}
      <div className="flex items-center gap-6 text-sm text-muted">

        {/* REGION */}
        <div className="flex items-center gap-2">
          <Globe size={14} />
          {organization?.region || "us-east-1"}
        </div>

        {/* USER DROPDOWN */}
        <div ref={dropdownRef} className="relative">

          <div
            onClick={() => setOpen(!open)}
            className="flex items-center gap-3 cursor-pointer"
          >
            {/* USER TEXT */}
            <div className="text-right hidden sm:block">
              <div className="text-xs text-muted">
                {organization?.name || "No Org"}
              </div>
              <div className="text-sm font-medium text-white">
                {user?.email}
              </div>
            </div>

            {/* AVATAR */}
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-xs font-semibold text-white">
              {user?.email?.charAt(0).toUpperCase()}
            </div>

            <ChevronDown size={14} />
          </div>

          {/* DROPDOWN */}
          {open && (
            <div className="absolute right-0 mt-2 w-44 bg-panel border border-border rounded-lg shadow-lg p-2 z-50">

              {/* USER INFO */}
              <div className="px-3 py-2 border-b border-border">
                <div className="text-xs text-muted">
                  {organization?.name}
                </div>
                <div className="text-sm font-medium text-white truncate">
                  {user?.email}
                </div>
              </div>
              <div className="flex justify-end p-4">
                <ThemeToggle />
              </div>

              {/* ACTIONS */}
              <button
                onClick={() => navigate("/settings")}
                className="w-full text-left px-3 py-2 rounded hover:bg-surface text-sm"
              >
                Settings
              </button>

              <button
                onClick={handleLogout}
                className="w-full text-left px-3 py-2 rounded hover:bg-surface text-sm text-red-500"
              >
                Logout
              </button>

            </div>
          )}
        </div>

      </div>
    </div>
  );
}