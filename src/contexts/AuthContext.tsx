import React, { createContext, useContext, ReactNode } from "react";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "../authConfig";

interface AuthContextType {
  isAuthenticated: boolean;
  login: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { instance, accounts } = useMsal();

  const isAuthenticated = accounts.length > 0;

  const login = async () => {
    try {
      console.log("Attempting login...");
      await instance.loginPopup(loginRequest);
      console.log("Login successful!");
    } catch (error) {
      console.error("Login error:", error);
    }
  };

  const logout = () => {
    instance.logoutPopup();
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
