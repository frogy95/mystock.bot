"use client";

/**
 * 인증 가드 컴포넌트
 * 토큰이 없으면 /login으로 리다이렉트한다.
 * useEffect 기반으로 Zustand SSR hydration 불일치를 방지한다.
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const token = useAuthStore((state) => state.token);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated && !token) {
      router.replace("/login");
    }
  }, [hydrated, token, router]);

  // hydration 완료 전 또는 미인증 시 빈 화면 (깜빡임 방지)
  if (!hydrated || !token) return null;

  return <>{children}</>;
}
