"use client";

import { useQuery } from "@tanstack/react-query";
import { mockSystemSettings } from "@/lib/mock";
import type { SystemSettings } from "@/lib/mock/types";

// Mock API 지연 시뮬레이션
function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** 시스템 설정 조회 훅 */
export function useSystemSettings() {
  return useQuery<SystemSettings>({
    queryKey: ["settings", "system"],
    queryFn: async () => {
      await delay(300);
      return mockSystemSettings;
    },
  });
}
