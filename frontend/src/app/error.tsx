"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

// Next.js App Router 세그먼트 에러 바운더리
export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    // 에러 콘솔 로깅
    console.error("[ErrorBoundary]", error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <h2 className="text-xl font-semibold text-destructive">
        오류가 발생했습니다
      </h2>
      <p className="max-w-md text-sm text-muted-foreground">
        {error.message || "예기치 않은 오류가 발생했습니다. 다시 시도해주세요."}
      </p>
      <Button onClick={reset} variant="outline">
        다시 시도
      </Button>
    </div>
  );
}
