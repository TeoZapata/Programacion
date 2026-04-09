import { apiGet, apiPost } from "@/services/http";

import type { AuthTokenResponse, AuthUser, LoginPayload, RegisterPayload } from "@/features/auth/types";

export function login(payload: LoginPayload): Promise<AuthTokenResponse> {
  return apiPost<AuthTokenResponse>("/auth/login", payload);
}

export function register(payload: RegisterPayload): Promise<AuthUser> {
  return apiPost<AuthUser>("/auth/register", payload);
}

export function fetchCurrentUser(token: string): Promise<AuthUser> {
  return apiGet<AuthUser>("/auth/me", token);
}
