"use client";

import { cn } from "@/lib/utils";
import { formatPercent, formatChange } from "@/lib/format";

interface PriceChangeBadgeProps {
  changeRate: number;
  changePrice?: number;
  showPrice?: boolean;
  size?: "sm" | "md" | "lg";
}

// 한국 주식 관례: 상승=빨간색, 하락=파란색
export function PriceChangeBadge({
  changeRate,
  changePrice,
  showPrice = false,
  size = "md",
}: PriceChangeBadgeProps) {
  const isPositive = changeRate > 0;
  const isNegative = changeRate < 0;

  const sizeClasses = {
    sm: "text-xs px-1.5 py-0.5",
    md: "text-sm px-2 py-0.5",
    lg: "text-base px-2.5 py-1",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md font-medium",
        sizeClasses[size],
        isPositive && "bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400",
        isNegative && "bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400",
        !isPositive && !isNegative && "bg-muted text-muted-foreground"
      )}
    >
      {showPrice && changePrice !== undefined && (
        <span>{formatChange(changePrice)}</span>
      )}
      <span>{formatPercent(changeRate)}</span>
    </span>
  );
}
