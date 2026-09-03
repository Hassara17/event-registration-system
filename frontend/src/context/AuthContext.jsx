import { createContext, useContext, useEffect, useState } from "react";
import {
  loginUser,
  getCurrentUser,
  registerUser,
} from "../api/auth.api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem("access_token");

      // No token -> user is not logged in
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();

        console.log("Authenticated user:", currentUser);

        setUser(currentUser);
        localStorage.setItem("user", JSON.stringify(currentUser));
      } catch (error) {
        console.error("Authentication failed:", error);

        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    const data = await loginUser(email, password);

    localStorage.setItem("access_token", data.access_token);

    const currentUser = await getCurrentUser();

    setUser(currentUser);
    localStorage.setItem("user", JSON.stringify(currentUser));

    return currentUser;
  };

  const register = async (name, email, password) => {
    return await registerUser(name, email, password);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {loading ? (
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "Arial, sans-serif",
            fontSize: "18px",
          }}
        >
          Loading application...
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};