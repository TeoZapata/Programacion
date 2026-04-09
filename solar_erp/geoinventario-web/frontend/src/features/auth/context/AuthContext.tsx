import { createContext, PropsWithChildren, useContext, useEffect, useState } from "react";

import {
  fetchCurrentUser,
  login as loginRequest,
  register as registerRequest,
} from "@/features/auth/services/authService";
import type { AuthUser, LoginPayload, RegisterPayload } from "@/features/auth/types";

type AuthContextValue = {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  token: string | null;
  user: AuthUser | null;
};

const AUTH_STORAGE_KEY = "geoinventario.auth.token";

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(AUTH_STORAGE_KEY));
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(Boolean(localStorage.getItem(AUTH_STORAGE_KEY)));

  useEffect(() => {
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    void fetchCurrentUser(token)
      .then((currentUser) => {
        setUser(currentUser);
      })
      .catch(() => {
        localStorage.removeItem(AUTH_STORAGE_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [token]);

  async function login(payload: LoginPayload): Promise<void> {
    const response = await loginRequest(payload);
    localStorage.setItem(AUTH_STORAGE_KEY, response.access_token);
    setToken(response.access_token);
    setUser(response.user);
    setIsLoading(false);
  }

  async function register(payload: RegisterPayload): Promise<void> {
    await registerRequest(payload);
    await login({ email: payload.email, password: payload.password });
  }

  async function refreshUser(): Promise<void> {
    if (!token) {
      setUser(null);
      return;
    }

    const currentUser = await fetchCurrentUser(token);
    setUser(currentUser);
  }

  function logout(): void {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    setToken(null);
    setUser(null);
    setIsLoading(false);
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: Boolean(token && user),
        isLoading,
        login,
        logout,
        refreshUser,
        register,
        token,
        user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
