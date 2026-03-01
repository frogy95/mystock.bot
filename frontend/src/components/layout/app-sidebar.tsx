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

const navItems = [
  { href: "/dashboard", label: "대시보드", icon: LayoutDashboard },
  { href: "/watchlist", label: "관심종목", icon: BookMarked },
  { href: "/strategy", label: "전략", icon: Cpu },
  { href: "/backtest", label: "백테스팅", icon: BarChart2 },
  { href: "/orders", label: "주문내역", icon: ClipboardList },
  { href: "/settings", label: "설정", icon: Settings },
];

export function AppSidebar() {
  const pathname = usePathname();

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
