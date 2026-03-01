"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Trash2, FolderPlus } from "lucide-react";
import { PriceChangeBadge } from "@/components/common/price-change-badge";
import { useWatchlistStore } from "@/stores/watchlist-store";
import { sellStrategyOptions } from "@/lib/mock/portfolio";
import { formatKRW, formatVolume, formatKRWCompact } from "@/lib/format";

export function WatchlistGroupTabs() {
  const {
    groups,
    activeGroupId,
    setActiveGroup,
    removeItem,
    assignStrategy,
    addGroup,
    removeGroup,
  } = useWatchlistStore();
  const [newGroupName, setNewGroupName] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleAddGroup = () => {
    if (newGroupName.trim()) {
      addGroup(newGroupName.trim());
      setNewGroupName("");
      setDialogOpen(false);
    }
  };

  return (
    <Tabs value={activeGroupId} onValueChange={setActiveGroup} className="w-full">
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        <TabsList>
          {groups.map((group) => (
            <TabsTrigger key={group.id} value={group.id}>
              {group.name}
              <Badge variant="secondary" className="ml-1.5 text-xs h-5 px-1.5">
                {group.items.length}
              </Badge>
            </TabsTrigger>
          ))}
        </TabsList>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="gap-1">
              <FolderPlus className="h-3.5 w-3.5" />
              그룹 추가
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>관심종목 그룹 추가</DialogTitle>
              <DialogDescription>
                새로운 관심종목 그룹의 이름을 입력하세요.
              </DialogDescription>
            </DialogHeader>
            <Input
              placeholder="그룹명 (예: IT, 금융, 에너지)"
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddGroup()}
            />
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>취소</Button>
              <Button onClick={handleAddGroup}>추가</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {groups.map((group) => (
        <TabsContent key={group.id} value={group.id}>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>종목명</TableHead>
                <TableHead className="text-right">현재가</TableHead>
                <TableHead className="text-right">등락률</TableHead>
                <TableHead className="text-right">거래량</TableHead>
                <TableHead className="text-right">시가총액</TableHead>
                <TableHead className="text-right">PER</TableHead>
                <TableHead>전략</TableHead>
                <TableHead className="w-10"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {group.items.length > 0 ? (
                group.items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {item.symbol} | {item.market}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono text-sm">
                      {formatKRW(item.currentPrice)}
                    </TableCell>
                    <TableCell className="text-right">
                      <PriceChangeBadge
                        changeRate={item.changeRate}
                        changePrice={item.changePrice}
                        showPrice
                        size="sm"
                      />
                    </TableCell>
                    <TableCell className="text-right text-sm font-mono">
                      {formatVolume(item.volume)}
                    </TableCell>
                    <TableCell className="text-right text-sm font-mono">
                      {item.marketCap > 0 ? formatKRWCompact(item.marketCap * 100_000_000) : "-"}
                    </TableCell>
                    <TableCell className="text-right text-sm font-mono">
                      {item.per ? item.per.toFixed(1) : "-"}
                    </TableCell>
                    <TableCell>
                      <Select
                        value={item.assignedStrategy ?? "none"}
                        onValueChange={(value) =>
                          assignStrategy(group.id, item.id, value === "none" ? null : value)
                        }
                      >
                        <SelectTrigger className="h-8 text-xs w-[140px]">
                          <SelectValue placeholder="전략 선택" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">미설정</SelectItem>
                          {sellStrategyOptions.map((opt) => (
                            <SelectItem key={opt.value} value={opt.value}>
                              {opt.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-muted-foreground hover:text-destructive"
                        onClick={() => removeItem(group.id, item.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground h-24">
                    이 그룹에 등록된 종목이 없습니다. 위 검색을 이용해 종목을 추가하세요.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>

          {groups.length > 1 && (
            <div className="flex justify-end mt-4">
              <Button
                variant="outline"
                size="sm"
                className="text-destructive hover:bg-destructive/10"
                onClick={() => removeGroup(group.id)}
              >
                <Trash2 className="h-3.5 w-3.5 mr-1" />
                그룹 삭제
              </Button>
            </div>
          )}
        </TabsContent>
      ))}
    </Tabs>
  );
}
