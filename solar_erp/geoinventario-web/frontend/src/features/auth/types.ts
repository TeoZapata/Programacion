export type UserRole = "admin" | "manager" | "operator" | "viewer";

export type AuthUser = {
  created_at: string;
  email: string;
  full_name: string;
  id: number;
  is_active: boolean;
  role: UserRole;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  full_name: string;
  password: string;
};

export type AuthTokenResponse = {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
};
