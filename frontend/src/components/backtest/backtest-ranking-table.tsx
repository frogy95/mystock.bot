"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { BacktestRankingEntry, StockStatusAPI } from "@/hooks/use-backtest";
import { apiClient } from "@/lib/api/client";
import { useState } from "react";

interface BacktestRankingTableProps {
  ranking: BacktestRankingEntry[];
  stockStatus: StockStatusAPI | null;
  onApplyStrategy?: (strategyId: number, strategyName: string) => void;
}

/** 수익률 색상 */
function ReturnBadge({ value }: { value: number }) {
  const color = value > 0 ? "text-green-500" : value < 0 ? "text-red-500" : "text-muted-foreground";
  return <span className={`font-medium ${color}`}>{value >= 0 ? "+" : ""}{value.toFixed(2)}%</span>;
}

export function BacktestRankingTable({ ranking, stockStatus, onApplyStrategy }: BacktestRankingTableProps) {
  const [applyingId, setApplyingId] = useState<number | null>(null);
  const [applyStatus, setApplyStatus] = useState<Record<number, string>>({});

  const handleApply = async (entry: BacktestRankingEntry) => {
    if (!stockStatus) return;
    setApplyingId(entry.strategy_id);

    try {
      if (stockStatus.is_holding && stockStatus.holding_id) {
        // 보유 종목 → 매도 전략 업데이트
        await apiClient.put(`/api/v1/holdings/${stockStatus.holding_id}/sell-strategy`, {
          sell_strategy_id: entry.strategy_id,
        });
        setApplyStatus((prev) => ({ ...prev, [entry.strategy_id]: "보유 종목에 적용됨" }));
      } else if (stockStatus.is_watchlist && stockStatus.watchlist_items.length > 0) {
        // 관심종목 → 전략 매칭
        const firstItem = stockStatus.watchlist_items[0];
        await apiClient.put(`/api/v1/watchlist/items/${firstItem.item_id}/strategy`, {
          strategy_id: entry.strategy_id,
        });
        setApplyStatus((prev) => ({ ...prev, [entry.strategy_id]: "관심종목에 적용됨" }));
      }
      onApplyStrategy?.(entry.strategy_id, entry.strategy_name);
    } catch {
      setApplyStatus((prev) => ({ ...prev, [entry.strategy_id]: "적용 실패" }));
    } finally {
      setApplyingId(null);
    }
  };

  if (ranking.length === 0) return null;

  const canApply = stockStatus?.is_holding || stockStatus?.is_watchlist;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>전략 랭킹</CardTitle>
          <div className="flex gap-2">
            {stockStatus?.is_holding && (
              <Badge variant="destructive">보유중</Badge>
            )}
            {stockStatus?.is_watchlist && (
              <Badge variant="secondary">관심종목</Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">순위</TableHead>
              <TableHead>전략명</TableHead>
              <TableHead className="text-right">수익률</TableHead>
              <TableHead className="text-right">MDD</TableHead>
              <TableHead className="text-right">샤프</TableHead>
              <TableHead className="text-right">승률</TableHead>
              <TableHead className="text-right">스코어</TableHead>
              {canApply && <TableHead className="text-right">적용</TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {ranking.map((entry) => (
              <TableRow
                key={entry.strategy_id}
                className={entry.rank === 1 ? "bg-primary/5 font-medium" : ""}
              >
                <TableCell>
                  {entry.rank === 1 ? (
                    <span className="text-yellow-500 font-bold">🥇</span>
                  ) : entry.rank === 2 ? (
                    <span className="text-slate-400 font-bold">🥈</span>
                  ) : entry.rank === 3 ? (
                    <span className="text-amber-600 font-bold">🥉</span>
                  ) : (
                    <span className="text-muted-foreground">{entry.rank}</span>
                  )}
                </TableCell>
                <TableCell>
                  <span className="font-medium">{entry.strategy_name}</span>
                </TableCell>
                <TableCell className="text-right">
                  <ReturnBadge value={entry.total_return} />
                </TableCell>
                <TableCell className="text-right">
                  <span className="text-red-500">{entry.mdd.toFixed(2)}%</span>
                </TableCell>
                <TableCell className="text-right">{entry.sharpe_ratio.toFixed(2)}</TableCell>
                <TableCell className="text-right">{entry.win_rate.toFixed(1)}%</TableCell>
                <TableCell className="text-right">
                  <Badge variant={entry.rank === 1 ? "default" : "outline"}>
                    {entry.score.toFixed(1)}
                  </Badge>
                </TableCell>
                {canApply && (
                  <TableCell className="text-right">
                    {applyStatus[entry.strategy_id] ? (
                      <span className="text-xs text-muted-foreground">
                        {applyStatus[entry.strategy_id]}
                      </span>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={applyingId === entry.strategy_id}
                        onClick={() => handleApply(entry)}
                      >
                        {applyingId === entry.strategy_id ? "적용 중..." : "적용"}
                      </Button>
                    )}
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
