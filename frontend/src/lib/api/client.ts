/**
 * fetch 기반 API 클라이언트
 * 토큰 관리 및 GET/POST/PUT/DELETE 메서드를 제공한다.
 * 401 수신 시 refreshToken으로 자동 갱신을 시도한다.
 */

import { useAuthStore } from "@/stores/auth-store";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return useAuthStore.getState().token;
}

function buildHeaders(extra: Record<string, string> = {}): HeadersInit {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...extra,
  };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

/** 리프레시 토큰으로 액세스 토큰을 갱신하고 새 토큰을 반환한다. */
async function tryRefreshToken(): Promise<string | null> {
  const { refreshToken, setToken, logout } = useAuthStore.getState();
  if (!refreshToken) return null;
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) {
      logout();
      return null;
    }
    const data = await res.json();
    setToken(data.access_token);
    return data.access_token;
  } catch {
    logout();
    return null;
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: buildHeaders(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  // 401: 리프레시 시도 후 재요청
  if (response.status === 401 && typeof window !== "undefined") {
    if (window.location.pathname === "/login") {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail ?? `HTTP ${response.status}`);
    }

    const newToken = await tryRefreshToken();
    if (newToken) {
      // 갱신 성공 → 원래 요청 재시도
      const retryResponse = await fetch(`${API_BASE_URL}${path}`, {
        method,
        headers: buildHeaders(),
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
      if (retryResponse.ok) {
        return retryResponse.json() as Promise<T>;
      }
    }

    // 갱신 실패 → 로그아웃 + 리다이렉트
    useAuthStore.getState().logout();
    window.location.href = "/login";
    throw new Error("인증이 만료되었습니다.");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? `HTTP ${response.status}`);
  }

  // 204 No Content: 빈 응답 처리
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body: unknown) => request<T>("POST", path, body),
  put: <T>(path: string, body: unknown) => request<T>("PUT", path, body),
  delete: <T>(path: string) => request<T>("DELETE", path),
};
