import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "@/features/auth/context/AuthContext";

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <p className="status-panel">Validando sesion...</p>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
