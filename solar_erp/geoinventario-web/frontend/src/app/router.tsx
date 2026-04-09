import { createBrowserRouter, Navigate } from "react-router-dom";

import { ProtectedRoute } from "@/features/auth/components/ProtectedRoute";
import { LoginPage } from "@/features/auth/pages/LoginPage";
import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";

export const router = createBrowserRouter([
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: "/",
        element: <DashboardPage />,
      },
    ],
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
]);
