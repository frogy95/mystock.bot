"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import type { TelegramConfig } from "@/lib/mock/types";

interface TelegramFormProps {
  config: TelegramConfig;
  onUpdate: (config: TelegramConfig) => void;
}

export function TelegramForm({ config, onUpdate }: TelegramFormProps) {
  const [local, setLocal] = useState<TelegramConfig>(config);

  // 서버 데이터 동기화
  useEffect(() => setLocal(config), [config]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>텔레그램 알림</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 텔레그램 활성화 Switch */}
        <div className="flex items-center justify-between">
          <Label htmlFor="telegram-enabled" className="text-base font-medium">
            텔레그램 알림 활성화
          </Label>
          <Switch
            id="telegram-enabled"
            checked={local.enabled}
            onCheckedChange={(checked) => setLocal((prev) => ({ ...prev, enabled: checked }))}
          />
        </div>

        <Separator />

        {/* Bot Token 입력 */}
        <div className="space-y-2">
          <Label htmlFor="botToken">Bot Token</Label>
          <Input
            id="botToken"
            type="text"
            value={local.botToken}
            onChange={(e) => setLocal((prev) => ({ ...prev, botToken: e.target.value }))}
            placeholder="Bot Token을 입력하세요"
            disabled={!local.enabled}
          />
        </div>

        {/* Chat ID 입력 */}
        <div className="space-y-2">
          <Label htmlFor="chatId">Chat ID</Label>
          <Input
            id="chatId"
            type="text"
            value={local.chatId}
            onChange={(e) => setLocal((prev) => ({ ...prev, chatId: e.target.value }))}
            placeholder="Chat ID를 입력하세요"
            disabled={!local.enabled}
          />
        </div>

        <Separator />

        {/* 알림 설정 */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-muted-foreground">알림 설정</p>

          {/* 매매 신호 알림 */}
          <div className="flex items-center justify-between">
            <Label htmlFor="notify-signal" className="cursor-pointer">
              매매 신호 알림
            </Label>
            <Switch
              id="notify-signal"
              checked={local.notifyOnSignal}
              onCheckedChange={(checked) => setLocal((prev) => ({ ...prev, notifyOnSignal: checked }))}
              disabled={!local.enabled}
            />
          </div>

          {/* 주문 체결 알림 */}
          <div className="flex items-center justify-between">
            <Label htmlFor="notify-order" className="cursor-pointer">
              주문 체결 알림
            </Label>
            <Switch
              id="notify-order"
              checked={local.notifyOnOrder}
              onCheckedChange={(checked) => setLocal((prev) => ({ ...prev, notifyOnOrder: checked }))}
              disabled={!local.enabled}
            />
          </div>

          {/* 에러 알림 */}
          <div className="flex items-center justify-between">
            <Label htmlFor="notify-error" className="cursor-pointer">
              에러 알림
            </Label>
            <Switch
              id="notify-error"
              checked={local.notifyOnError}
              onCheckedChange={(checked) => setLocal((prev) => ({ ...prev, notifyOnError: checked }))}
              disabled={!local.enabled}
            />
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
