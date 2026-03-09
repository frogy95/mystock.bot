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
import { useSyncHoldings, useSilentSyncHoldings } from "@/hooks/use-holdings-mutations";
import { formatKRW } from "@/lib/format";
import { RefreshCw, Loader2 } from "lucide-react";

export function HoldingsTable() {
  const { data: holdings, isLoading, isError } = useHoldings();
  const { data: kisStatus } = useKisStatus();
  const { mutate: syncHoldings, isPending: isSyncing } = useSyncHoldings();
  const { mutate: silentSync } = useSilentSyncHoldings();
  const autoSyncTriggered = useRef(false);

  // 토큰이 유효할 때만 최초 1회 자동 동기화 (silent - 에러 토스트 없음)
  useEffect(() => {
    if (
      !autoSyncTriggered.current &&
      !isLoading &&
      kisStatus?.available &&
      kisStatus?.token_valid
    ) {
      autoSyncTriggered.current = true;
      silentSync();
    }
  }, [isLoading, holdings, kisStatus, silentSync]);

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
      {/* 토큰 미준비 상태: 대기 안내 인라인 메시지 */}
      {kisStatus?.available && !kisStatus?.token_valid && (
        <div className="px-6 pb-2 flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          KIS 토큰 발급 대기 중...
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-xs px-2"
            onClick={() => {
              autoSyncTriggered.current = false;
            }}
          >
            재확인
          </Button>
        </div>
      )}
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
                  {!kisStatus?.available
                    ? "KIS API가 연결되지 않았습니다. 설정에서 API 키를 입력해주세요."
                    : !kisStatus?.token_valid
                    ? "KIS 토큰 발급 대기 중입니다."
                    : "보유종목이 없습니다."}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
