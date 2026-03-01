"use client";

import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSidebarStore } from "@/stores/sidebar-store";

export function AppHeader() {
  const toggle = useSidebarStore((state) => state.toggle);

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

      <h1 className="text-sm font-medium text-muted-foreground">
        한국 주식 자동매매 봇
      </h1>
    </header>
  );
}
