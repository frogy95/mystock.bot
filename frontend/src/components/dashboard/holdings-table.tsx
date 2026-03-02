"use client";

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
import { PriceChangeBadge } from "@/components/common/price-change-badge";
import { TableRowSkeleton } from "@/components/common/loading-skeleton";
import { useHoldings } from "@/hooks/use-dashboard";
import { formatKRW } from "@/lib/format";

export function HoldingsTable() {
  const { data: holdings, isLoading } = useHoldings();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">보유종목</CardTitle>
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
            {isLoading ? (
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
