"use client";

/**
 * 경로별 조건부 레이아웃
 * /login: 사이드바/헤더 없이 children만 렌더링
 * 나머지: AuthGuard → AppLayout 래핑
 */
import { usePathname } from "next/navigation";
import { AppLayout } from "@/components/layout/app-layout";
import { AuthGuard } from "@/components/layout/auth-guard";

export function ConditionalLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname === "/login") {
    return <>{children}</>;
  }

  return (
    <AuthGuard>
      <AppLayout>{children}</AppLayout>
    </AuthGuard>
  );
}
