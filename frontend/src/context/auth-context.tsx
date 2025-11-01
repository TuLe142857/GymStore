import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { jwtDecode } from "jwt-decode";

interface DecodedToken {
  id: number;
  email: string;
  role: string;
  exp?: number;
}

interface AuthContextType {
  isLoggedIn: boolean;
  token: string | null;
  role: string | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem("access_token"));
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      try {
        const decoded: DecodedToken = jwtDecode(token);
        setRole(decoded.role || null);
      } catch (error) {
        console.error("Invalid token:", error);
        setRole(null);
      }
    } else {
      setRole(null);
    }
  }, [token]);

  const isLoggedIn = !!token;

  const login = (newToken: string) => {
    localStorage.setItem("access_token", newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, token, role, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
