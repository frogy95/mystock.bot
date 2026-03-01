"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { PriceChangeBadge } from "@/components/common/price-change-badge";
import { useStockSearch } from "@/hooks/use-watchlist";
import { useWatchlistStore } from "@/stores/watchlist-store";
import { formatKRW } from "@/lib/format";
import type { StockQuote } from "@/lib/mock/types";
import { Plus } from "lucide-react";

export function StockSearch() {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const { data: results, isLoading } = useStockSearch(query);
  const { activeGroupId, addItem } = useWatchlistStore();

  const handleSelect = (stock: StockQuote) => {
    addItem(activeGroupId, stock);
    setQuery("");
    setOpen(false);
  };

  return (
    <Popover open={open && query.length > 0} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="종목코드 또는 종목명으로 검색..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setOpen(true);
            }}
            onFocus={() => query.length > 0 && setOpen(true)}
            className="pl-9"
          />
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0" align="start">
        <ScrollArea className="max-h-[300px]">
          {isLoading ? (
            <div className="p-4 text-sm text-muted-foreground text-center">검색 중...</div>
          ) : results && results.length > 0 ? (
            <div className="divide-y">
              {results.map((stock) => (
                <div
                  key={stock.symbol}
                  className="flex items-center justify-between p-3 hover:bg-accent cursor-pointer transition-colors"
                  onClick={() => handleSelect(stock)}
                >
                  <div>
                    <p className="font-medium text-sm">{stock.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {stock.symbol} | {stock.market}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <p className="text-sm font-mono">{formatKRW(stock.currentPrice)}</p>
                      <PriceChangeBadge changeRate={stock.changeRate} size="sm" />
                    </div>
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); handleSelect(stock); }}>
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : query.length > 0 ? (
            <div className="p-4 text-sm text-muted-foreground text-center">검색 결과가 없습니다.</div>
          ) : null}
        </ScrollArea>
      </PopoverContent>
    </Popover>
  );
}
