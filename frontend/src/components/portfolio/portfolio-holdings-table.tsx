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
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PriceChangeBadge } from "@/components/common/price-change-badge";
import { TableRowSkeleton } from "@/components/common/loading-skeleton";
import { usePortfolioHoldings } from "@/hooks/use-portfolio";
import type { HoldingAPI } from "@/hooks/use-portfolio";
import { formatKRW } from "@/lib/format";
import { Pencil, Check, X } from "lucide-react";

export function PortfolioHoldingsTable() {
  const { data: holdings, isLoading } = usePortfolioHoldings();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<{
    stopLossRate: string;
    takeProfitRate: string;
  }>({ stopLossRate: "", takeProfitRate: "" });

  const startEdit = (item: HoldingAPI) => {
    setEditingId(String(item.id));
    setEditValues({
      stopLossRate: item.stop_loss_rate?.toString() ?? "",
      takeProfitRate: item.take_profit_rate?.toString() ?? "",
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
                const isEditing = editingId === String(item.id);
                return (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{item.stock_name}</p>
                        <p className="text-xs text-muted-foreground">{item.stock_code}</p>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {formatKRW(item.avg_price)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {item.quantity.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {item.current_price != null ? formatKRW(item.current_price) : "-"}
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {item.total_value != null ? formatKRW(item.total_value) : "-"}
                    </TableCell>
                    <TableCell className="text-right">
                      <PriceChangeBadge changeRate={item.profit_loss_rate} />
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
                          {item.stop_loss_rate != null ? `${item.stop_loss_rate}%` : "-"}
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
                          {item.take_profit_rate != null ? `+${item.take_profit_rate}%` : "-"}
                        </span>
                      )}
                    </TableCell>

                    {/* 매도 전략 */}
                    <TableCell>
                      {item.sell_strategy_id != null ? (
                        <Badge variant="secondary" className="text-xs">
                          전략 #{item.sell_strategy_id}
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
