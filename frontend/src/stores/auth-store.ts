/**
 * 인증 상태 스토어
 * persist 미들웨어로 토큰을 localStorage에 저장한다.
 * 미들웨어 리다이렉트를 위해 auth-token 쿠키도 동기화한다.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

const DEMO_USERNAME = "__demo__";

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  username: string | null;
  role: string | null;
  userId: number | null;
  login: (token: string, username: string, refreshToken?: string) => void;
  logout: () => void;
  setToken: (token: string) => void;
  setRole: (role: string, userId: number) => void;
  isAuthenticated: () => boolean;
  isDemo: () => boolean;
}

function setCookie(name: string, value: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${name}=${value}; path=/; max-age=86400; SameSite=Lax`;
}

function deleteCookie(name: string) {
  if (typeof document === "undefined") return;
  document.cookie = `${name}=; path=/; max-age=0`;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      refreshToken: null,
      username: null,
      role: null,
      userId: null,

      login: (token: string, username: string, refreshToken?: string) => {
        // 재로그인 시 이전 role/userId가 잔존하지 않도록 명시적 초기화
        set({ token, username, refreshToken: refreshToken ?? null, role: null, userId: null });
        setCookie("auth-token", token);
      },

      logout: () => {
        set({ token: null, username: null, refreshToken: null, role: null, userId: null });
        deleteCookie("auth-token");
      },

      // 액세스 토큰만 갱신 (리프레시 후 호출)
      setToken: (token: string) => {
        set({ token });
        setCookie("auth-token", token);
      },

      // role과 userId 저장 (/auth/me 호출 후 저장)
      setRole: (role: string, userId: number) => {
        set({ role, userId });
      },

      isAuthenticated: () => get().token !== null,

      isDemo: () => get().username === DEMO_USERNAME,
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        username: state.username,
        role: state.role,
        userId: state.userId,
      }),
      onRehydrateStorage: () => (state) => {
        // localStorage에서 복원 후 쿠키도 동기화
        if (state?.token) {
          setCookie("auth-token", state.token);
        }
      },
    }
  )
);
