"use client";

import { LogOut, Menu, User } from "lucide-react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useSidebarStore } from "@/stores/sidebar-store";
import { useAuthStore } from "@/stores/auth-store";

export function AppHeader() {
  const toggle = useSidebarStore((state) => state.toggle);
  const { username, logout, isDemo } = useAuthStore();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.replace("/login");
  }

  const demo = isDemo();
  const displayName = demo ? "데모 사용자" : (username ?? "");

  return (
    <header className="h-14 border-b flex items-center px-4 shrink-0 bg-background gap-3">
      {/* 모바일 햄버거 메뉴 */}
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={toggle}
        aria-label="메뉴 열기"
      >
        <Menu className="h-5 w-5" />
      </Button>

      <h1 className="text-sm font-medium text-muted-foreground flex-1">
        한국 주식 자동매매 봇
      </h1>

      {/* 우측: 데모 뱃지 + 사용자명 + 로그아웃 */}
      <div className="flex items-center gap-2">
        {demo && (
          <Badge variant="secondary" className="text-xs">
            데모 모드
          </Badge>
        )}
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <User className="h-4 w-4" />
          <span className="hidden sm:inline">{displayName}</span>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleLogout}
          aria-label="로그아웃"
          title="로그아웃"
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
