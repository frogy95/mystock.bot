"use client";

import { useSettingsStore } from "@/stores/settings-store";
import { AutoTradeControl } from "@/components/settings/auto-trade-control";
import { KisApiForm } from "@/components/settings/kis-api-form";
import { TelegramForm } from "@/components/settings/telegram-form";
import { TradingTimeForm } from "@/components/settings/trading-time-form";
import { SafetySettingsForm } from "@/components/settings/safety-settings-form";
import { EmergencySellButton } from "@/components/settings/emergency-sell-button";
import { Separator } from "@/components/ui/separator";

export default function SettingsPage() {
  // 설정 상태 및 액션 가져오기
  const { settings, updateKisApi, updateTelegram, updateTradingTime, updateSafety, toggleAutoTrade } =
    useSettingsStore();

  // 긴급 전체 매도 확인 핸들러
  const handleEmergencySell = () => {
    console.log("긴급 전체 매도 실행");
    // 실제 구현 시: 백엔드 API 호출
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* 페이지 제목 */}
      <div>
        <h2 className="text-2xl font-semibold mb-1">설정</h2>
        <p className="text-muted-foreground">봇 및 API 설정을 관리합니다.</p>
      </div>

      {/* 자동매매 마스터 스위치 (최우선 표시) */}
      <AutoTradeControl
        isEnabled={settings.autoTradeEnabled}
        onToggle={toggleAutoTrade}
      />

      {/* KIS API 설정 */}
      <KisApiForm config={settings.kisApi} onUpdate={updateKisApi} />

      {/* 텔레그램 알림 설정 */}
      <TelegramForm config={settings.telegram} onUpdate={updateTelegram} />

      {/* 매매 시간 설정 */}
      <TradingTimeForm
        config={settings.tradingTime}
        onUpdate={updateTradingTime}
      />

      {/* 안전장치 설정 */}
      <SafetySettingsForm config={settings.safety} onUpdate={updateSafety} />

      {/* 위험 섹션 구분선 */}
      <Separator className="my-2" />

      {/* 긴급 전체 매도 (최하단 위험 섹션) */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-destructive">위험 구역</p>
        <EmergencySellButton onConfirm={handleEmergencySell} />
      </div>
    </div>
  );
}
