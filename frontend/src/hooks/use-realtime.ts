"use client";

import { useEffect, useRef, useState } from "react";
import { WSClient } from "@/lib/ws-client";

/** 실시간 시세 데이터 타입 */
export interface RealtimeQuote {
  symbol: string;
  price: number;
  change: number;
  changeRate: number;
  volume: number;
}

/**
 * 실시간 시세 구독 훅
 * WebSocket 연결 자동 관리 및 재연결 처리
 * symbols 배열이 비어있으면 연결하지 않는다.
 */
export function useRealtimeQuotes(symbols: string[]) {
  const [quotes, setQuotes] = useState<Record<string, RealtimeQuote>>({});
  const [connected, setConnected] = useState(false);
  const clientRef = useRef<WSClient | null>(null);

  // symbols 배열을 의존성으로 안정적으로 사용하기 위해 문자열로 변환
  const symbolsKey = symbols.join(",");

  useEffect(() => {
    if (symbols.length === 0) return;

    const wsUrl =
      process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
    const client = new WSClient(
      `${wsUrl}/api/v1/ws/quotes?symbols=${symbolsKey}`
    );
    clientRef.current = client;

    // 연결 확인 이벤트 핸들러
    const unsubConnected = client.on("connected", () => setConnected(true));

    // 시세 업데이트 이벤트 핸들러
    const unsubQuote = client.on("quote", (data: unknown) => {
      const msg = data as { symbol: string; data: Record<string, unknown> };
      if (msg.symbol && msg.data) {
        setQuotes((prev) => ({
          ...prev,
          [msg.symbol]: {
            symbol: msg.symbol,
            price: Number(msg.data.price ?? msg.data.stck_prpr ?? 0),
            change: Number(msg.data.change ?? msg.data.prdy_vrss ?? 0),
            changeRate: Number(
              msg.data.change_rate ?? msg.data.prdy_ctrt ?? 0
            ),
            volume: Number(msg.data.volume ?? msg.data.acml_vol ?? 0),
          },
        }));
      }
    });

    client.connect();

    // 컴포넌트 언마운트 또는 symbols 변경 시 정리
    return () => {
      unsubConnected();
      unsubQuote();
      client.disconnect();
      setConnected(false);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbolsKey]);

  return { quotes, connected };
}
