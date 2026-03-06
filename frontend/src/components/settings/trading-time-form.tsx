"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import type { TradingTimeConfig } from "@/lib/mock/types";

interface TradingTimeFormProps {
  config: TradingTimeConfig;
  onUpdate: (config: TradingTimeConfig) => void;
}

export function TradingTimeForm({ config, onUpdate }: TradingTimeFormProps) {
  const [local, setLocal] = useState<TradingTimeConfig>(config);

  // 서버 데이터 동기화
  useEffect(() => setLocal(config), [config]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>매매 시간</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 시작 시간 */}
        <div className="space-y-2">
          <Label htmlFor="startTime">시작 시간</Label>
          <Input
            id="startTime"
            type="time"
            value={local.startTime}
            onChange={(e) => setLocal((prev) => ({ ...prev, startTime: e.target.value }))}
            className="w-36"
          />
        </div>

        {/* 종료 시간 */}
        <div className="space-y-2">
          <Label htmlFor="endTime">종료 시간</Label>
          <Input
            id="endTime"
            type="time"
            value={local.endTime}
            onChange={(e) => setLocal((prev) => ({ ...prev, endTime: e.target.value }))}
            className="w-36"
          />
        </div>

        {/* 장 마감 전 거래 제외 (분) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>장 마감 전 거래 제외</Label>
            <span className="text-sm font-medium tabular-nums">
              {local.excludeLastMinutes}분
            </span>
          </div>
          <Slider
            min={0}
            max={60}
            step={5}
            value={[local.excludeLastMinutes]}
            onValueChange={(values: number[]) =>
              setLocal((prev) => ({ ...prev, excludeLastMinutes: values[0] }))
            }
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>0분</span>
            <span>60분</span>
          </div>
        </div>

        {/* 저장 버튼 */}
        <Button onClick={() => onUpdate(local)} className="w-full">
          저장
        </Button>
      </CardContent>
    </Card>
  );
}
