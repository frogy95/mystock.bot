import type { SystemSettings } from "./types";

/**
 * 시스템 설정 Mock 데이터 (기본값)
 * - KIS API: 모의투자 모드 (실전 전환 전 테스트용)
 * - 텔레그램: 알림 활성화
 * - 매매 시간: 장 시작 후 30분 ~ 장 마감 30분 전
 * - 안전장치: 보수적 기본값 설정
 */
export const mockSystemSettings: SystemSettings = {
  kisApi: {
    // 실제 서비스에서는 환경변수로 관리, Mock에서는 마스킹 처리
    appKey: "DEMO_APP_KEY_XXXXXXXX",
    appSecret: "DEMO_APP_SECRET_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    mode: "paper", // 모의투자 모드 (기본값)
  },
  telegram: {
    botToken: "0000000000:DEMO_BOT_TOKEN_XXXXXXXXXXXXXXXXXXXXXXXX",
    chatId: "-1001234567890",
    enabled: true,
    notifyOnSignal: true,  // 매매 신호 발생 시 알림
    notifyOnOrder: true,   // 주문 체결 시 알림
    notifyOnError: true,   // 오류 발생 시 알림
  },
  tradingTime: {
    startTime: "09:30",        // 장 시작(09:00) 후 30분 경과 시점부터 매매
    endTime: "15:00",          // 장 마감(15:30) 30분 전까지 매매
    excludeLastMinutes: 30,    // 장 마감 전 30분 거래 제외
  },
  safety: {
    dailyLossLimit: 3,       // 일일 손실 한도 3% (초과 시 당일 자동매매 중단)
    maxOrdersPerDay: 10,     // 일일 최대 주문 횟수 10회
    maxPositionRatio: 20,    // 종목당 최대 비중 20% (분산투자 강제)
    stopLossRate: 5,         // 기본 손절률 -5% (종목별 손절률 미설정 시 적용)
  },
  autoTradeEnabled: false, // 자동매매 비활성화 (기본값: 수동 확인 후 활성화)
};
