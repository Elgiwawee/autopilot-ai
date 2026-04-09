// src/context/AuthContext.jsx

import { createContext, useContext, useEffect, useState } from "react";
import { fetchMe } from "../api/auth.api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const me = await fetchMe();

        setUser({
          email: me.user.email,
          organizations: me.organizations,
        });

      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, [token]);

  async function login(jwt) {
    localStorage.setItem("token", jwt);
    setToken(jwt);

    try {
      const me = await fetchMe();

      setUser({
        email: me.user.email,
        organizations: me.organizations,
      });

    } catch {
      logout();
    }
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        loading,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
