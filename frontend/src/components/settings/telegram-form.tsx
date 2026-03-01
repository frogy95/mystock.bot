"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import type { TelegramConfig } from "@/lib/mock/types";

interface TelegramFormProps {
  config: TelegramConfig;
  onUpdate: (updates: Partial<TelegramConfig>) => void;
}

export function TelegramForm({ config, onUpdate }: TelegramFormProps) {
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
            checked={config.enabled}
            onCheckedChange={(checked) => onUpdate({ enabled: checked })}
          />
        </div>

        <Separator />

        {/* Bot Token 입력 */}
        <div className="space-y-2">
          <Label htmlFor="botToken">Bot Token</Label>
          <Input
            id="botToken"
            type="text"
            value={config.botToken}
            onChange={(e) => onUpdate({ botToken: e.target.value })}
            placeholder="Bot Token을 입력하세요"
            disabled={!config.enabled}
          />
        </div>

        {/* Chat ID 입력 */}
        <div className="space-y-2">
          <Label htmlFor="chatId">Chat ID</Label>
          <Input
            id="chatId"
            type="text"
            value={config.chatId}
            onChange={(e) => onUpdate({ chatId: e.target.value })}
            placeholder="Chat ID를 입력하세요"
            disabled={!config.enabled}
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
              checked={config.notifyOnSignal}
              onCheckedChange={(checked) =>
                onUpdate({ notifyOnSignal: checked })
              }
              disabled={!config.enabled}
            />
          </div>

          {/* 주문 체결 알림 */}
          <div className="flex items-center justify-between">
            <Label htmlFor="notify-order" className="cursor-pointer">
              주문 체결 알림
            </Label>
            <Switch
              id="notify-order"
              checked={config.notifyOnOrder}
              onCheckedChange={(checked) =>
                onUpdate({ notifyOnOrder: checked })
              }
              disabled={!config.enabled}
            />
          </div>

          {/* 에러 알림 */}
          <div className="flex items-center justify-between">
            <Label htmlFor="notify-error" className="cursor-pointer">
              에러 알림
            </Label>
            <Switch
              id="notify-error"
              checked={config.notifyOnError}
              onCheckedChange={(checked) =>
                onUpdate({ notifyOnError: checked })
              }
              disabled={!config.enabled}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
