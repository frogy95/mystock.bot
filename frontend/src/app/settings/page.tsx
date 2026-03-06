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
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import { AlertTriangle } from "lucide-react";
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

      {/* 탭 구조 */}
      <Tabs defaultValue="api">
        <TabsList className="w-full">
          <TabsTrigger value="api" className="flex-1">API 연동</TabsTrigger>
          <TabsTrigger value="trade" className="flex-1">매매 설정</TabsTrigger>
          <TabsTrigger value="alert" className="flex-1">알림 &amp; 위험</TabsTrigger>
        </TabsList>

        {/* API 연동 탭 */}
        <TabsContent value="api" className="space-y-4 mt-4">
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
        </TabsContent>

        {/* 매매 설정 탭 */}
        <TabsContent value="trade" className="space-y-4 mt-4">
          <TradingTimeForm
            config={parseTradingTimeConfig(settings)}
            onUpdate={(cfg) => {
              const items = buildItems({
                trading_start_time: cfg.startTime,
                trading_end_time: cfg.endTime,
                trading_exclude_last_minutes: cfg.excludeLastMinutes,
              });
              updateSettings.mutate(items);
            }}
          />
          <SafetySettingsForm
            config={parseSafetyConfig(settings)}
            onUpdate={(cfg) => {
              const items = buildItems({
                safety_daily_loss_limit: cfg.dailyLossLimit,
                safety_max_orders_per_day: cfg.maxOrdersPerDay,
                safety_max_position_ratio: cfg.maxPositionRatio,
                safety_stop_loss_rate: cfg.stopLossRate,
              });
              updateSettings.mutate(items);
            }}
          />
        </TabsContent>

        {/* 알림 & 위험 탭 */}
        <TabsContent value="alert" className="space-y-4 mt-4">
          <TelegramForm
            config={parseTelegramConfig(settings)}
            onUpdate={(cfg) => {
              const items = buildItems({
                telegram_bot_token: cfg.botToken,
                telegram_chat_id: cfg.chatId,
                telegram_enabled: cfg.enabled,
                telegram_notify_signal: cfg.notifyOnSignal,
                telegram_notify_order: cfg.notifyOnOrder,
                telegram_notify_error: cfg.notifyOnError,
              });
              updateSettings.mutate(items);
            }}
          />

          {/* 위험 구역 Card */}
          <Card className="border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950">
            <div className="flex items-center justify-between px-6 py-4">
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2 text-red-700 dark:text-red-400 font-semibold text-base">
                  <AlertTriangle className="h-5 w-5 shrink-0" />
                  위험 구역
                </div>
                <p className="text-sm text-red-600 dark:text-red-500">
                  아래 작업은 되돌릴 수 없습니다. 신중하게 사용하세요.
                </p>
              </div>
              <EmergencySellButton onConfirm={() => emergencySell.mutate()} />
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
