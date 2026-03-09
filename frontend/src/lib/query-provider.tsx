"use client";

import { MutationCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        // Mutation 글로벌 에러 핸들러: 모든 뮤테이션 에러를 toast로 표시
        mutationCache: new MutationCache({
          onError: (error, _variables, _context, mutation) => {
            console.error("[MutationCache] 뮤테이션 에러:", error);
            // silent: true meta가 설정된 경우 토스트 생략 (자동 동기화 등)
            if (!mutation.meta?.silent) {
              toast.error(error.message || "요청 처리 중 오류가 발생했습니다.");
            }
          },
        }),
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1분
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
