"use client";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  description?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    label: string;
  };
  className?: string;
}

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  className,
}: StatCardProps) {
  return (
    <Card className={cn("py-4", className)}>
      <CardContent className="px-4">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
        </div>
        <div className="mt-2">
          <p className="text-2xl font-bold">{value}</p>
          {trend && (
            <p
              className={cn(
                "text-xs mt-1",
                (trend.value ?? 0) > 0 && "text-red-600",
                (trend.value ?? 0) < 0 && "text-blue-600",
                (trend.value ?? 0) === 0 && "text-muted-foreground"
              )}
            >
              {(trend.value ?? 0) > 0 ? "+" : ""}
              {(trend.value ?? 0).toFixed(2)}% {trend.label}
            </p>
          )}
          {description && (
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
