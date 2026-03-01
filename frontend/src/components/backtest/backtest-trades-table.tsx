"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { BacktestTrade } from "@/lib/mock/types";

interface BacktestTradesTableProps {
  trades: BacktestTrade[];
}

export function BacktestTradesTable({ trades }: BacktestTradesTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>거래 내역</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {/* 모바일에서 가로 스크롤 허용 */}
        <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>날짜</TableHead>
              <TableHead>구분</TableHead>
              <TableHead className="text-right">가격</TableHead>
              <TableHead className="text-right">수량</TableHead>
              <TableHead className="text-right">금액</TableHead>
              <TableHead className="text-right">손익</TableHead>
              <TableHead>판단 근거</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trades.map((trade) => (
              <TableRow key={trade.id}>
                {/* 날짜 */}
                <TableCell className="whitespace-nowrap">{trade.date}</TableCell>

                {/* 구분: BUY 빨간색, SELL 파란색 */}
                <TableCell>
                  {trade.type === "BUY" ? (
                    <Badge variant="destructive">매수</Badge>
                  ) : (
                    <Badge className="bg-blue-500 hover:bg-blue-600 text-white">
                      매도
                    </Badge>
                  )}
                </TableCell>

                {/* 가격 */}
                <TableCell className="text-right">
                  {trade.price.toLocaleString("ko-KR")}원
                </TableCell>

                {/* 수량 */}
                <TableCell className="text-right">{trade.quantity}주</TableCell>

                {/* 금액 */}
                <TableCell className="text-right">
                  {trade.amount.toLocaleString("ko-KR")}원
                </TableCell>

                {/* 손익 + 수익률 */}
                <TableCell className="text-right">
                  {trade.profitLoss === null ? (
                    <span className="text-muted-foreground">-</span>
                  ) : (
                    <span
                      className={
                        trade.profitLoss > 0 ? "text-red-600" : "text-blue-600"
                      }
                    >
                      {trade.profitLoss > 0 ? "+" : ""}
                      {trade.profitLoss.toLocaleString("ko-KR")}원
                      <br />
                      <span className="text-xs">
                        {trade.profitRate !== null
                          ? `${trade.profitRate > 0 ? "+" : ""}${trade.profitRate.toFixed(2)}%`
                          : "-"}
                      </span>
                    </span>
                  )}
                </TableCell>

                {/* 판단 근거 */}
                <TableCell className="text-xs text-muted-foreground max-w-xs truncate">
                  {trade.reason}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        </div>
      </CardContent>
    </Card>
  );
}
