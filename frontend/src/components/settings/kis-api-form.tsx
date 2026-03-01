"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import type { KisApiConfig } from "@/lib/mock/types";

interface KisApiFormProps {
  config: KisApiConfig;
  onUpdate: (updates: Partial<KisApiConfig>) => void;
}

export function KisApiForm({ config, onUpdate }: KisApiFormProps) {
  // 로컬 편집 상태 (저장 버튼 클릭 시 반영)
  const [localConfig, setLocalConfig] = useState<KisApiConfig>(config);
  // App Key 표시/숨김 토글
  const [showAppKey, setShowAppKey] = useState(false);
  // App Secret 표시/숨김 토글
  const [showAppSecret, setShowAppSecret] = useState(false);

  const handleSave = () => {
    onUpdate(localConfig);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>KIS API 설정</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* App Key 입력 */}
        <div className="space-y-2">
          <Label htmlFor="appKey">App Key</Label>
          <div className="flex gap-2">
            <Input
              id="appKey"
              type={showAppKey ? "text" : "password"}
              value={localConfig.appKey}
              onChange={(e) =>
                setLocalConfig((prev) => ({ ...prev, appKey: e.target.value }))
              }
              placeholder="App Key를 입력하세요"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowAppKey((prev) => !prev)}
            >
              {showAppKey ? "숨기기" : "표시"}
            </Button>
          </div>
        </div>

        {/* App Secret 입력 */}
        <div className="space-y-2">
          <Label htmlFor="appSecret">App Secret</Label>
          <div className="flex gap-2">
            <Input
              id="appSecret"
              type={showAppSecret ? "text" : "password"}
              value={localConfig.appSecret}
              onChange={(e) =>
                setLocalConfig((prev) => ({
                  ...prev,
                  appSecret: e.target.value,
                }))
              }
              placeholder="App Secret을 입력하세요"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowAppSecret((prev) => !prev)}
            >
              {showAppSecret ? "숨기기" : "표시"}
            </Button>
          </div>
        </div>

        {/* 모의/실전 선택 */}
        <div className="space-y-2">
          <Label>투자 모드</Label>
          <RadioGroup
            value={localConfig.mode}
            onValueChange={(value) =>
              setLocalConfig((prev) => ({
                ...prev,
                mode: value as "paper" | "real",
              }))
            }
            className="flex gap-6"
          >
            <div className="flex items-center gap-2">
              <RadioGroupItem value="paper" id="mode-paper" />
              <Label htmlFor="mode-paper" className="cursor-pointer">
                모의투자
              </Label>
            </div>
            <div className="flex items-center gap-2">
              <RadioGroupItem value="real" id="mode-real" />
              <Label htmlFor="mode-real" className="cursor-pointer">
                실전투자
              </Label>
            </div>
          </RadioGroup>

          {/* 모의투자 선택 시 경고 배지 표시 */}
          {localConfig.mode === "paper" && (
            <Badge className="bg-yellow-500 text-yellow-950 hover:bg-yellow-500">
              모의투자 모드 — 실제 주문이 실행되지 않습니다
            </Badge>
          )}
        </div>

        {/* 저장 버튼 */}
        <Button onClick={handleSave} className="w-full">
          저장
        </Button>
      </CardContent>
    </Card>
  );
}
