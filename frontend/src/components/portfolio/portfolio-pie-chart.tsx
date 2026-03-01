"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { usePortfolioPieData } from "@/hooks/use-portfolio";
import { formatKRWCompact } from "@/lib/format";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

// Recharts Tooltip 커스텀
function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: { percentage: number } }>;
}) {
  if (!active || !payload || payload.length === 0) return null;
  const data = payload[0];
  return (
    <div className="bg-popover border rounded-lg shadow-md p-3 text-sm">
      <p className="font-medium">{data.name}</p>
      <p className="text-muted-foreground">
        {formatKRWCompact(data.value)} ({data.payload.percentage.toFixed(1)}%)
      </p>
    </div>
  );
}

export function PortfolioPieChart() {
  const { data: pieData, isLoading } = usePortfolioPieData();

  if (isLoading || !pieData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">포트폴리오 구성</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[250px] w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">포트폴리오 구성</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              dataKey="value"
              nameKey="name"
            >
              {pieData.map((entry) => (
                <Cell key={entry.symbol} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* 범례 */}
        <div className="flex flex-wrap justify-center gap-3 mt-4">
          {pieData.map((entry) => (
            <div key={entry.symbol} className="flex items-center gap-1.5 text-xs">
              <div
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span>{entry.name}</span>
              <span className="text-muted-foreground">{entry.percentage.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
