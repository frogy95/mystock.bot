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
  username: string | null;
  login: (token: string, username: string) => void;
  logout: () => void;
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
      username: null,

      login: (token: string, username: string) => {
        set({ token, username });
        setCookie("auth-token", token);
      },

      logout: () => {
        set({ token: null, username: null });
        deleteCookie("auth-token");
      },

      isAuthenticated: () => get().token !== null,

      isDemo: () => get().username === DEMO_USERNAME,
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        token: state.token,
        username: state.username,
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
