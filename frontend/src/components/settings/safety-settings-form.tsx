"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import type { SafetyConfig } from "@/lib/mock/types";

interface SafetySettingsFormProps {
  config: SafetyConfig;
  onUpdate: (updates: Partial<SafetyConfig>) => void;
}

export function SafetySettingsForm({ config, onUpdate }: SafetySettingsFormProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>안전장치</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 일일 손실 한도 (%) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>일일 손실 한도</Label>
            <span className="text-sm font-medium tabular-nums">
              {config.dailyLossLimit}%
            </span>
          </div>
          <Slider
            min={1}
            max={20}
            step={0.5}
            value={[config.dailyLossLimit]}
            onValueChange={(values: number[]) =>
              onUpdate({ dailyLossLimit: values[0] })
            }
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>1%</span>
            <span>20%</span>
          </div>
        </div>

        {/* 일일 최대 주문 횟수 */}
        <div className="space-y-2">
          <Label htmlFor="maxOrdersPerDay">일일 최대 주문 횟수</Label>
          <Input
            id="maxOrdersPerDay"
            type="number"
            min={1}
            max={50}
            value={config.maxOrdersPerDay}
            onChange={(e) =>
              onUpdate({ maxOrdersPerDay: Number(e.target.value) })
            }
            className="w-28"
          />
        </div>

        {/* 종목당 최대 비중 (%) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>종목당 최대 비중</Label>
            <span className="text-sm font-medium tabular-nums">
              {config.maxPositionRatio}%
            </span>
          </div>
          <Slider
            min={5}
            max={50}
            step={5}
            value={[config.maxPositionRatio]}
            onValueChange={(values: number[]) =>
              onUpdate({ maxPositionRatio: values[0] })
            }
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>5%</span>
            <span>50%</span>
          </div>
        </div>

        {/* 기본 손절률 (%) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>기본 손절률</Label>
            <span className="text-sm font-medium tabular-nums">
              {config.stopLossRate}%
            </span>
          </div>
          <Slider
            min={1}
            max={20}
            step={0.5}
            value={[config.stopLossRate]}
            onValueChange={(values: number[]) =>
              onUpdate({ stopLossRate: values[0] })
            }
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>1%</span>
            <span>20%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
