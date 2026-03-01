"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart2,
  BookMarked,
  ClipboardList,
  Cpu,
  LayoutDashboard,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useSidebarStore } from "@/stores/sidebar-store";

const navItems = [
  { href: "/dashboard", label: "대시보드", icon: LayoutDashboard },
  { href: "/watchlist", label: "관심종목", icon: BookMarked },
  { href: "/strategy", label: "전략", icon: Cpu },
  { href: "/backtest", label: "백테스팅", icon: BarChart2 },
  { href: "/orders", label: "주문내역", icon: ClipboardList },
  { href: "/settings", label: "설정", icon: Settings },
];

function SidebarContent() {
  const pathname = usePathname();
  const close = useSidebarStore((state) => state.close);

  return (
    <aside className="w-56 shrink-0 border-r bg-background flex flex-col h-full">
      {/* 로고 */}
      <div className="h-14 flex items-center px-4 border-b">
        <span className="font-bold text-lg">mystock.bot</span>
      </div>

      {/* 네비게이션 */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            onClick={close}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
              pathname === href
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

export function AppSidebar() {
  const { isOpen, close } = useSidebarStore();

  return (
    <>
      {/* 데스크톱: 항상 표시 */}
      <div className="hidden md:flex">
        <SidebarContent />
      </div>

      {/* 모바일: 오버레이 + 슬라이드 인 */}
      {isOpen && (
        <>
          {/* 오버레이 배경 */}
          <div
            className="fixed inset-0 z-40 bg-black/50 md:hidden"
            onClick={close}
          />
          {/* 사이드바 패널 */}
          <div className="fixed inset-y-0 left-0 z-50 md:hidden flex">
            <SidebarContent />
          </div>
        </>
      )}
    </>
  );
}
