"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PriceChangeBadge } from "@/components/common/price-change-badge";
import { TableRowSkeleton } from "@/components/common/loading-skeleton";
import { usePortfolioHoldings } from "@/hooks/use-portfolio";
import { sellStrategyOptions } from "@/lib/mock/portfolio";
import { formatKRW } from "@/lib/format";
import { Pencil, Check, X } from "lucide-react";
import type { HoldingItem } from "@/lib/mock/types";

export function PortfolioHoldingsTable() {
  const { data: holdings, isLoading } = usePortfolioHoldings();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<{
    stopLossRate: string;
    takeProfitRate: string;
    sellStrategy: string;
  }>({ stopLossRate: "", takeProfitRate: "", sellStrategy: "" });

  const startEdit = (item: HoldingItem) => {
    setEditingId(item.symbol);
    setEditValues({
      stopLossRate: item.stopLossRate?.toString() ?? "",
      takeProfitRate: item.takeProfitRate?.toString() ?? "",
      sellStrategy: item.sellStrategy ?? "none",
    });
  };

  const cancelEdit = () => setEditingId(null);

  const saveEdit = () => {
    // Mock 단계: 콘솔 출력만 (Phase 3에서 API 연동)
    console.log("저장:", editingId, editValues);
    setEditingId(null);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">보유종목 상세</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>종목명</TableHead>
              <TableHead className="text-right">매입가</TableHead>
              <TableHead className="text-right">수량</TableHead>
              <TableHead className="text-right">현재가</TableHead>
              <TableHead className="text-right">평가금액</TableHead>
              <TableHead className="text-right">수익률</TableHead>
              <TableHead className="text-right">손절</TableHead>
              <TableHead className="text-right">익절</TableHead>
              <TableHead>매도 전략</TableHead>
              <TableHead className="w-16"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRowSkeleton key={i} columns={10} />
              ))
            ) : holdings && holdings.length > 0 ? (
              holdings.map((item) => {
                const isEditing = editingId === item.symbol;
                return (
                  <TableRow key={item.symbol}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-xs text-muted-foreground">{item.symbol}</p>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {formatKRW(item.avgPrice)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {item.quantity.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {formatKRW(item.currentPrice)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {formatKRW(item.evalAmount)}
                    </TableCell>
                    <TableCell className="text-right">
                      <PriceChangeBadge changeRate={item.profitRate} />
                    </TableCell>

                    {/* 손절률 */}
                    <TableCell className="text-right">
                      {isEditing ? (
                        <Input
                          type="number"
                          value={editValues.stopLossRate}
                          onChange={(e) =>
                            setEditValues((v) => ({ ...v, stopLossRate: e.target.value }))
                          }
                          className="h-7 w-16 text-xs text-right"
                          placeholder="-5"
                        />
                      ) : (
                        <span className="text-sm font-mono text-blue-600">
                          {item.stopLossRate ? `${item.stopLossRate}%` : "-"}
                        </span>
                      )}
                    </TableCell>

                    {/* 익절률 */}
                    <TableCell className="text-right">
                      {isEditing ? (
                        <Input
                          type="number"
                          value={editValues.takeProfitRate}
                          onChange={(e) =>
                            setEditValues((v) => ({ ...v, takeProfitRate: e.target.value }))
                          }
                          className="h-7 w-16 text-xs text-right"
                          placeholder="15"
                        />
                      ) : (
                        <span className="text-sm font-mono text-red-600">
                          {item.takeProfitRate ? `+${item.takeProfitRate}%` : "-"}
                        </span>
                      )}
                    </TableCell>

                    {/* 매도 전략 */}
                    <TableCell>
                      {isEditing ? (
                        <Select
                          value={editValues.sellStrategy}
                          onValueChange={(value) =>
                            setEditValues((v) => ({ ...v, sellStrategy: value }))
                          }
                        >
                          <SelectTrigger className="h-7 text-xs w-[130px]">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="none">미설정</SelectItem>
                            {sellStrategyOptions.map((opt) => (
                              <SelectItem key={opt.value} value={opt.label}>
                                {opt.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : item.sellStrategy ? (
                        <Badge variant="secondary" className="text-xs">
                          {item.sellStrategy}
                        </Badge>
                      ) : (
                        <span className="text-xs text-muted-foreground">미설정</span>
                      )}
                    </TableCell>

                    {/* 편집 버튼 */}
                    <TableCell>
                      {isEditing ? (
                        <div className="flex gap-1">
                          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={saveEdit}>
                            <Check className="h-3.5 w-3.5 text-green-600" />
                          </Button>
                          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={cancelEdit}>
                            <X className="h-3.5 w-3.5 text-muted-foreground" />
                          </Button>
                        </div>
                      ) : (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => startEdit(item)}
                        >
                          <Pencil className="h-3.5 w-3.5 text-muted-foreground" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={10} className="text-center text-muted-foreground h-24">
                  보유종목이 없습니다.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
