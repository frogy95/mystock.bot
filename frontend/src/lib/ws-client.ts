"use client";

/**
 * WebSocket 클라이언트 유틸리티
 * 자동 재연결 기능 포함
 * 서버 연결 불가 시 지수 백오프 방식으로 재시도한다.
 */

type MessageHandler = (data: unknown) => void;

export class WSClient {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private reconnectDelay = 3000;
  private shouldReconnect = true;

  constructor(url: string) {
    this.url = url;
  }

  /** WebSocket 연결을 시작한다. */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log("WebSocket 연결됨");
      // 재연결 성공 시 지연 시간 초기화
      this.reconnectDelay = 3000;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const type = data.type as string;
        // 타입별 핸들러 실행
        const handlers = this.handlers.get(type) ?? [];
        handlers.forEach((h) => h(data));
        // 전체 메시지 핸들러 (*) 실행
        (this.handlers.get("*") ?? []).forEach((h) => h(data));
      } catch (e) {
        console.warn("WebSocket 메시지 파싱 오류:", e);
      }
    };

    this.ws.onclose = () => {
      // 자동 재연결 (지수 백오프: 최대 30초)
      if (this.shouldReconnect) {
        setTimeout(() => this.connect(), this.reconnectDelay);
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
      }
    };

    this.ws.onerror = (err) => {
      console.warn("WebSocket 오류:", err);
    };
  }

  /** WebSocket 연결을 종료한다. */
  disconnect(): void {
    this.shouldReconnect = false;
    this.ws?.close();
  }

  /**
   * 특정 타입의 메시지 핸들러를 등록한다.
   * @returns 핸들러 해제 함수
   */
  on(type: string, handler: MessageHandler): () => void {
    const existing = this.handlers.get(type) ?? [];
    this.handlers.set(type, [...existing, handler]);
    // 언마운트 시 핸들러 해제용 클린업 함수 반환
    return () => {
      const updated = (this.handlers.get(type) ?? []).filter(
        (h) => h !== handler
      );
      this.handlers.set(type, updated);
    };
  }

  /** WebSocket으로 데이터를 전송한다. */
  send(data: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  /** 종목 코드 목록을 구독한다. */
  subscribe(symbols: string[]): void {
    this.send({ type: "subscribe", symbols });
  }
}
