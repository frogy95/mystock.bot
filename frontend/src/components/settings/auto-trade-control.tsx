"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";

interface AutoTradeControlProps {
  isEnabled: boolean;
  onToggle: () => void;
}

export function AutoTradeControl({ isEnabled, onToggle }: AutoTradeControlProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-2xl">자동매매</CardTitle>
            <CardDescription>
              자동매매를 활성화하면 전략이 자동으로 주문을 실행합니다
            </CardDescription>
          </div>
          {/* 활성화 상태 배지 */}
          {isEnabled ? (
            <Badge className="bg-red-500 text-white hover:bg-red-500 text-sm px-3 py-1">
              실행 중
            </Badge>
          ) : (
            <Badge variant="secondary" className="text-sm px-3 py-1">
              중지됨
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {/* 자동매매 마스터 스위치 */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">
            {isEnabled
              ? "자동매매가 활성화되어 있습니다. 전략 조건 충족 시 자동으로 주문합니다."
              : "자동매매가 비활성화되어 있습니다. 수동으로 주문을 실행하세요."}
          </span>
          <Switch
            checked={isEnabled}
            onCheckedChange={onToggle}
            className="scale-125"
          />
        </div>
      </CardContent>
    </Card>
  );
}
