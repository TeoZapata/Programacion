const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

type RequestOptions = {
  body?: unknown;
  headers?: Record<string, string>;
  method?: "GET" | "POST";
  token?: string | null;
};

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Keep the default message if the response body is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function apiGet<T>(path: string, token?: string | null): Promise<T> {
  return apiRequest<T>(path, { method: "GET", token });
}

export function apiPost<T>(path: string, body: unknown, token?: string | null): Promise<T> {
  return apiRequest<T>(path, { method: "POST", body, token });
}
