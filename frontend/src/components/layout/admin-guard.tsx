"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

interface AdminGuardProps {
  children: React.ReactNode;
}

/** 관리자 전용 라우트 보호 컴포넌트 - admin 역할이 아닌 경우 접근을 차단한다 */
export function AdminGuard({ children }: AdminGuardProps) {
  const router = useRouter();
  const role = useAuthStore((state) => state.role);
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    if (!token) {
      router.replace("/login");
      return;
    }
    if (role !== null && role !== "admin") {
      router.replace("/dashboard");
    }
  }, [role, token, router]);

  if (!token || (role !== null && role !== "admin")) {
    return null;
  }

  return <>{children}</>;
}
