"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";

interface OrdersFilterProps {
  statusFilter: string;
  orderTypeFilter: string;
  symbolFilter: string;
  onStatusFilterChange: (v: string) => void;
  onOrderTypeFilterChange: (v: string) => void;
  onSymbolFilterChange: (v: string) => void;
}

/** 주문 내역 필터 컴포넌트 */
export function OrdersFilter({
  statusFilter,
  orderTypeFilter,
  symbolFilter,
  onStatusFilterChange,
  onOrderTypeFilterChange,
  onSymbolFilterChange,
}: OrdersFilterProps) {
  return (
    <Card>
      <CardContent className="pt-4 pb-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:flex-wrap">
          {/* 상태 필터 탭: 전체 / 미체결 / 체결완료 / 취소 */}
          <Tabs value={statusFilter} onValueChange={onStatusFilterChange}>
            <TabsList>
              <TabsTrigger value="ALL">전체</TabsTrigger>
              <TabsTrigger value="PENDING">미체결</TabsTrigger>
              <TabsTrigger value="FILLED">체결완료</TabsTrigger>
              <TabsTrigger value="CANCELLED">취소</TabsTrigger>
            </TabsList>
          </Tabs>

          {/* 매수/매도 필터 */}
          <Select value={orderTypeFilter} onValueChange={onOrderTypeFilterChange}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="전체" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">전체</SelectItem>
              <SelectItem value="BUY">매수</SelectItem>
              <SelectItem value="SELL">매도</SelectItem>
            </SelectContent>
          </Select>

          {/* 종목코드 검색 */}
          <Input
            className="w-[160px]"
            placeholder="종목코드 검색"
            value={symbolFilter}
            onChange={(e) => onSymbolFilterChange(e.target.value)}
          />
        </div>
      </CardContent>
    </Card>
  );
}
