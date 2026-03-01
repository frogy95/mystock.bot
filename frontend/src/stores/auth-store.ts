/**
 * 인증 상태 스토어
 * persist 미들웨어로 토큰을 localStorage에 저장한다.
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  username: string | null;
  login: (token: string, username: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      username: null,

      login: (token: string, username: string) => {
        set({ token, username });
      },

      logout: () => {
        set({ token: null, username: null });
      },

      isAuthenticated: () => get().token !== null,
    }),
    {
      name: "auth-storage",
      // token만 persist (보안: username도 포함)
      partialize: (state) => ({
        token: state.token,
        username: state.username,
      }),
    }
  )
);
