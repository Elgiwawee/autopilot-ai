// src/routes/ProtectedRoute.jsx

import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const { isAuthenticated, loading, user } = useAuth();

  // ✅ wait for auth to resolve
  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  // ✅ check BOTH token + user
  if (!isAuthenticated || !user) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
