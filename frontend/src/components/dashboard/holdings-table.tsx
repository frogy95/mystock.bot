"use client";

import { useEffect, useRef } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PriceChangeBadge } from "@/components/common/price-change-badge";
import { TableRowSkeleton } from "@/components/common/loading-skeleton";
import { useHoldings, useKisStatus } from "@/hooks/use-dashboard";
import { useSyncHoldings } from "@/hooks/use-holdings-mutations";
import { formatKRW } from "@/lib/format";
import { RefreshCw } from "lucide-react";

export function HoldingsTable() {
  const { data: holdings, isLoading, isError } = useHoldings();
  const { data: kisStatus } = useKisStatus();
  const { mutate: syncHoldings, isPending: isSyncing } = useSyncHoldings();
  const autoSyncTriggered = useRef(false);

  // 보유종목이 비어있고 KIS 연결 상태이면 최초 1회 자동 동기화
  useEffect(() => {
    if (
      !autoSyncTriggered.current &&
      !isLoading &&
      holdings?.length === 0 &&
      kisStatus?.available
    ) {
      autoSyncTriggered.current = true;
      syncHoldings();
    }
  }, [isLoading, holdings, kisStatus, syncHoldings]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">보유종목</CardTitle>
        {kisStatus?.available && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => syncHoldings()}
            disabled={isSyncing}
          >
            <RefreshCw className={`h-4 w-4 mr-1.5 ${isSyncing ? "animate-spin" : ""}`} />
            {isSyncing ? "동기화 중..." : "KIS 동기화"}
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>종목명</TableHead>
              <TableHead className="text-right">현재가</TableHead>
              <TableHead className="text-right">수량</TableHead>
              <TableHead className="text-right">매입가</TableHead>
              <TableHead className="text-right">평가금액</TableHead>
              <TableHead className="text-right">수익률</TableHead>
              <TableHead>전략</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isError ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-destructive h-24">
                  보유종목을 불러오지 못했습니다.
                </TableCell>
              </TableRow>
            ) : isLoading || isSyncing ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRowSkeleton key={i} columns={7} />
              ))
            ) : holdings && holdings.length > 0 ? (
              holdings.map((item) => (
                <TableRow key={item.stock_code}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{item.stock_name}</p>
                      <p className="text-xs text-muted-foreground">{item.stock_code}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {item.current_price != null ? formatKRW(item.current_price) : "-"}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {item.quantity.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatKRW(item.avg_price)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {item.total_value != null ? formatKRW(item.total_value) : "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    <PriceChangeBadge changeRate={item.profit_loss_rate ?? undefined} />
                  </TableCell>
                  <TableCell>
                    {item.sell_strategy_id != null ? (
                      <Badge variant="secondary" className="text-xs">
                        전략 #{item.sell_strategy_id}
                      </Badge>
                    ) : (
                      <span className="text-xs text-muted-foreground">미설정</span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground h-24">
                  {kisStatus?.available
                    ? "보유종목이 없습니다."
                    : "KIS API가 연결되지 않았습니다. 설정에서 API 키를 입력해주세요."}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
