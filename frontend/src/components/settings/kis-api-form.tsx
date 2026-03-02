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

/** password 필드 표시/숨김 토글이 포함된 입력 컴포넌트 */
function SecretInput({
  id,
  value,
  onChange,
  placeholder,
}: {
  id: string;
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
}) {
  const [show, setShow] = useState(false);
  return (
    <div className="flex gap-2">
      <Input
        id={id}
        type={show ? "text" : "password"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
      <Button type="button" variant="outline" size="sm" onClick={() => setShow((p) => !p)}>
        {show ? "숨기기" : "표시"}
      </Button>
    </div>
  );
}

export function KisApiForm({ config, onUpdate }: KisApiFormProps) {
  const [local, setLocal] = useState<KisApiConfig>(config);

  const set = (field: keyof KisApiConfig) => (value: string) =>
    setLocal((prev) => ({ ...prev, [field]: value }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>KIS API 설정</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 모의투자 앱 키 */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-muted-foreground">모의투자 앱 키 (주문/잔고)</p>
          <div className="space-y-2">
            <Label htmlFor="vtsAppKey">App Key</Label>
            <SecretInput
              id="vtsAppKey"
              value={local.vtsAppKey}
              onChange={set("vtsAppKey")}
              placeholder="모의투자 App Key"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="vtsAppSecret">App Secret</Label>
            <SecretInput
              id="vtsAppSecret"
              value={local.vtsAppSecret}
              onChange={set("vtsAppSecret")}
              placeholder="모의투자 App Secret"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="vtsAccountNumber">계좌번호</Label>
            <Input
              id="vtsAccountNumber"
              value={local.vtsAccountNumber}
              onChange={(e) => set("vtsAccountNumber")(e.target.value)}
              placeholder="모의투자 계좌번호 (예: 50123456-01)"
            />
          </div>
        </div>

        {/* 실전투자 앱 키 */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-muted-foreground">
            실전투자 앱 키 (시세 조회 + 실전 주문/잔고)
          </p>
          <p className="text-xs text-blue-600 bg-blue-50 rounded px-2 py-1">
            시세(현재가·차트·지수)는 실전 키로만 조회됩니다. 모의투자 모드에서도 반드시 입력하세요.
          </p>
          <div className="space-y-2">
            <Label htmlFor="realAppKey">App Key</Label>
            <SecretInput
              id="realAppKey"
              value={local.realAppKey}
              onChange={set("realAppKey")}
              placeholder="실전투자 App Key"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="realAppSecret">App Secret</Label>
            <SecretInput
              id="realAppSecret"
              value={local.realAppSecret}
              onChange={set("realAppSecret")}
              placeholder="실전투자 App Secret"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="realAccountNumber">계좌번호</Label>
            <Input
              id="realAccountNumber"
              value={local.realAccountNumber}
              onChange={(e) => set("realAccountNumber")(e.target.value)}
              placeholder="실전 계좌번호 (예: 50123456-01)"
            />
          </div>
        </div>

        {/* HTS ID */}
        <div className="space-y-2">
          <Label htmlFor="htsId">HTS ID</Label>
          <Input
            id="htsId"
            value={local.htsId}
            onChange={(e) => set("htsId")(e.target.value)}
            placeholder="eFriend Plus 로그인 ID"
          />
        </div>

        {/* 투자 모드 */}
        <div className="space-y-2">
          <Label>투자 모드</Label>
          <RadioGroup
            value={local.mode}
            onValueChange={(value) =>
              setLocal((prev) => ({ ...prev, mode: value as "vts" | "real" }))
            }
            className="flex gap-6"
          >
            <div className="flex items-center gap-2">
              <RadioGroupItem value="vts" id="mode-vts" />
              <Label htmlFor="mode-vts" className="cursor-pointer">
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

          {local.mode === "vts" && (
            <Badge className="bg-yellow-500 text-yellow-950 hover:bg-yellow-500">
              모의투자 모드 — 실제 주문이 실행되지 않습니다
            </Badge>
          )}
          {local.mode === "real" && (
            <Badge variant="destructive">
              실전투자 모드 — 실제 자금이 거래됩니다 ⚠️
            </Badge>
          )}
        </div>

        {/* 저장 버튼 */}
        <Button onClick={() => onUpdate(local)} className="w-full">
          저장
        </Button>
      </CardContent>
    </Card>
  );
}
