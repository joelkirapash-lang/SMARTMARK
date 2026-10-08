import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api, getAccessToken, setTokens, clearTokens } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [school, setSchool] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadMe = useCallback(async () => {
    if (!getAccessToken()) {
      setLoading(false);
      return;
    }
    try {
      const data = await api.get("/auth/me");
      setUser(data.user);
      setSchool(data.school);
    } catch {
      clearTokens();
      setUser(null);
      setSchool(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMe();
  }, [loadMe]);

  const login = async (smartmark_email, password) => {
    const data = await api.post("/auth/login", { smartmark_email, password });
    setTokens(data);
    setUser(data.user);
    await loadMe();
    return data;
  };

  const registerSchool = async (payload) => {
    const data = await api.post("/schools/register", payload);
    setTokens(data);
    setUser(data.user);
    setSchool(data.school);
    return data;
  };

  const acceptInvitation = async (token, password, confirm_password) => {
    const data = await api.post("/invitations/accept", { token, password, confirm_password });
    setTokens(data);
    setUser(data.user);
    await loadMe();
    return data;
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    setSchool(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, school, loading, login, registerSchool, acceptInvitation, logout, refresh: loadMe }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
