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
                <TableRow key={item.symbol}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{item.name}</p>
                      <p className="text-xs text-muted-foreground">{item.symbol}</p>
                    </div>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatKRW(item.currentPrice)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {item.quantity.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatKRW(item.avgPrice)}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatKRW(item.evalAmount)}
                  </TableCell>
                  <TableCell className="text-right">
                    <PriceChangeBadge changeRate={item.profitRate} />
                  </TableCell>
                  <TableCell>
                    {item.sellStrategy ? (
                      <Badge variant="secondary" className="text-xs">
                        {item.sellStrategy}
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
