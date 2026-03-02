"use client";

import { useEffect } from "react";

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

// Next.js 앱 전체 크래시 처리용 글로벌 에러 바운더리
// global-error는 루트 layout.tsx를 대체하므로 html/body 태그 필수
export default function GlobalError({ error, reset }: GlobalErrorProps) {
  useEffect(() => {
    // 글로벌 에러 콘솔 로깅
    console.error("[GlobalErrorBoundary]", error);
  }, [error]);

  return (
    <html lang="ko">
      <body>
        <div
          style={{
            display: "flex",
            minHeight: "100vh",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "1rem",
            textAlign: "center",
            fontFamily: "sans-serif",
            padding: "1rem",
          }}
        >
          <h1 style={{ fontSize: "1.5rem", fontWeight: 600, color: "#ef4444" }}>
            앱 오류가 발생했습니다
          </h1>
          <p style={{ fontSize: "0.875rem", color: "#6b7280", maxWidth: "28rem" }}>
            {error.message || "예기치 않은 오류로 앱을 불러올 수 없습니다."}
          </p>
          <button
            onClick={reset}
            style={{
              padding: "0.5rem 1.25rem",
              border: "1px solid #d1d5db",
              borderRadius: "0.375rem",
              background: "white",
              cursor: "pointer",
              fontSize: "0.875rem",
            }}
          >
            새로고침
          </button>
        </div>
      </body>
    </html>
  );
}
