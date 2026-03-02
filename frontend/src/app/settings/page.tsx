"use client";

import {
  useSystemSettings,
  useSafetyStatus,
  useToggleAutoTrade,
  useEmergencySell,
  useUpdateSettings,
} from "@/hooks/use-settings";
import type { SettingItemAPI } from "@/hooks/use-settings";
import { AutoTradeControl } from "@/components/settings/auto-trade-control";
import { KisApiForm } from "@/components/settings/kis-api-form";
import { TelegramForm } from "@/components/settings/telegram-form";
import { TradingTimeForm } from "@/components/settings/trading-time-form";
import { SafetySettingsForm } from "@/components/settings/safety-settings-form";
import { EmergencySellButton } from "@/components/settings/emergency-sell-button";
import { Separator } from "@/components/ui/separator";
import type {
  KisApiConfig,
  TelegramConfig,
  TradingTimeConfig,
  SafetyConfig,
} from "@/lib/mock/types";

/** SettingItemAPI[] 배열에서 특정 key 값 추출 */
function getVal(settings: SettingItemAPI[], key: string, defaultValue = ""): string {
  return settings.find((s) => s.setting_key === key)?.setting_value ?? defaultValue;
}

/** SettingItemAPI[] → KisApiConfig 파싱 */
function parseKisApiConfig(s: SettingItemAPI[]): KisApiConfig {
  return {
    vtsAppKey: getVal(s, "kis_vts_app_key"),
    vtsAppSecret: getVal(s, "kis_vts_app_secret"),
    vtsAccountNumber: getVal(s, "kis_vts_account_number"),
    realAppKey: getVal(s, "kis_real_app_key"),
    realAppSecret: getVal(s, "kis_real_app_secret"),
    realAccountNumber: getVal(s, "kis_real_account_number"),
    htsId: getVal(s, "kis_hts_id"),
    mode: getVal(s, "kis_mode", "vts") as "vts" | "real",
  };
}

/** SettingItemAPI[] → TelegramConfig 파싱 */
function parseTelegramConfig(s: SettingItemAPI[]): TelegramConfig {
  return {
    botToken: getVal(s, "telegram_bot_token"),
    chatId: getVal(s, "telegram_chat_id"),
    enabled: getVal(s, "telegram_enabled", "false") === "true",
    notifyOnSignal: getVal(s, "telegram_notify_signal", "false") === "true",
    notifyOnOrder: getVal(s, "telegram_notify_order", "false") === "true",
    notifyOnError: getVal(s, "telegram_notify_error", "false") === "true",
  };
}

/** SettingItemAPI[] → TradingTimeConfig 파싱 */
function parseTradingTimeConfig(s: SettingItemAPI[]): TradingTimeConfig {
  return {
    startTime: getVal(s, "trading_start_time", "09:30"),
    endTime: getVal(s, "trading_end_time", "15:00"),
    excludeLastMinutes: Number(getVal(s, "trading_exclude_last_minutes", "30")),
  };
}

/** SettingItemAPI[] → SafetyConfig 파싱 */
function parseSafetyConfig(s: SettingItemAPI[]): SafetyConfig {
  return {
    dailyLossLimit: Number(getVal(s, "safety_daily_loss_limit", "3")),
    maxOrdersPerDay: Number(getVal(s, "safety_max_orders_per_day", "10")),
    maxPositionRatio: Number(getVal(s, "safety_max_position_ratio", "20")),
    stopLossRate: Number(getVal(s, "safety_stop_loss_rate", "5")),
  };
}

/** 업데이트 필드 → SettingItemAPI[] 변환 */
function buildItems(updates: Record<string, string | number | boolean>): SettingItemAPI[] {
  return Object.entries(updates).map(([key, value]) => ({
    setting_key: key,
    setting_value: String(value),
    setting_type: "string",
  }));
}

export default function SettingsPage() {
  const { data: rawSettings, isLoading: isSettingsLoading, isError: isSettingsError } =
    useSystemSettings();
  const { data: safetyStatus, isLoading: isSafetyLoading } = useSafetyStatus();

  const toggleAutoTrade = useToggleAutoTrade();
  const emergencySell = useEmergencySell();
  const updateSettings = useUpdateSettings();

  if (isSettingsLoading || isSafetyLoading) {
    return <div className="max-w-3xl mx-auto"><p className="text-muted-foreground">로딩 중...</p></div>;
  }

  if (isSettingsError) {
    return <div className="max-w-3xl mx-auto"><p className="text-destructive">설정을 불러오는 중 오류가 발생했습니다.</p></div>;
  }

  const settings = rawSettings ?? [];
  const autoTradeEnabled = safetyStatus?.auto_trade_enabled ?? false;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* 페이지 제목 */}
      <div>
        <h2 className="text-2xl font-semibold mb-1">설정</h2>
        <p className="text-muted-foreground">봇 및 API 설정을 관리합니다.</p>
      </div>

      {/* 자동매매 마스터 스위치 */}
      <AutoTradeControl
        isEnabled={autoTradeEnabled}
        onToggle={() => toggleAutoTrade.mutate(!autoTradeEnabled)}
      />

      {/* KIS API 설정 */}
      <KisApiForm
        config={parseKisApiConfig(settings)}
        onUpdate={(updates) => {
          const items = buildItems({
            ...(updates.vtsAppKey !== undefined && { kis_vts_app_key: updates.vtsAppKey }),
            ...(updates.vtsAppSecret !== undefined && { kis_vts_app_secret: updates.vtsAppSecret }),
            ...(updates.vtsAccountNumber !== undefined && { kis_vts_account_number: updates.vtsAccountNumber }),
            ...(updates.realAppKey !== undefined && { kis_real_app_key: updates.realAppKey }),
            ...(updates.realAppSecret !== undefined && { kis_real_app_secret: updates.realAppSecret }),
            ...(updates.realAccountNumber !== undefined && { kis_real_account_number: updates.realAccountNumber }),
            ...(updates.htsId !== undefined && { kis_hts_id: updates.htsId }),
            ...(updates.mode !== undefined && { kis_mode: updates.mode }),
          });
          if (items.length > 0) updateSettings.mutate(items);
        }}
      />

      {/* 텔레그램 알림 설정 */}
      <TelegramForm
        config={parseTelegramConfig(settings)}
        onUpdate={(updates) => {
          const items = buildItems({
            ...(updates.botToken !== undefined && { telegram_bot_token: updates.botToken }),
            ...(updates.chatId !== undefined && { telegram_chat_id: updates.chatId }),
            ...(updates.enabled !== undefined && { telegram_enabled: updates.enabled }),
            ...(updates.notifyOnSignal !== undefined && { telegram_notify_signal: updates.notifyOnSignal }),
            ...(updates.notifyOnOrder !== undefined && { telegram_notify_order: updates.notifyOnOrder }),
            ...(updates.notifyOnError !== undefined && { telegram_notify_error: updates.notifyOnError }),
          });
          if (items.length > 0) updateSettings.mutate(items);
        }}
      />

      {/* 매매 시간 설정 */}
      <TradingTimeForm
        config={parseTradingTimeConfig(settings)}
        onUpdate={(updates) => {
          const items = buildItems({
            ...(updates.startTime !== undefined && { trading_start_time: updates.startTime }),
            ...(updates.endTime !== undefined && { trading_end_time: updates.endTime }),
            ...(updates.excludeLastMinutes !== undefined && { trading_exclude_last_minutes: updates.excludeLastMinutes }),
          });
          if (items.length > 0) updateSettings.mutate(items);
        }}
      />

      {/* 안전장치 설정 */}
      <SafetySettingsForm
        config={parseSafetyConfig(settings)}
        onUpdate={(updates) => {
          const items = buildItems({
            ...(updates.dailyLossLimit !== undefined && { safety_daily_loss_limit: updates.dailyLossLimit }),
            ...(updates.maxOrdersPerDay !== undefined && { safety_max_orders_per_day: updates.maxOrdersPerDay }),
            ...(updates.maxPositionRatio !== undefined && { safety_max_position_ratio: updates.maxPositionRatio }),
            ...(updates.stopLossRate !== undefined && { safety_stop_loss_rate: updates.stopLossRate }),
          });
          if (items.length > 0) updateSettings.mutate(items);
        }}
      />

      {/* 위험 섹션 */}
      <Separator className="my-2" />
      <div className="space-y-2">
        <p className="text-sm font-medium text-destructive">위험 구역</p>
        <EmergencySellButton onConfirm={() => emergencySell.mutate()} />
      </div>
    </div>
  );
}
