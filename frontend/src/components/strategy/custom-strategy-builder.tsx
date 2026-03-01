"use client";

import { CustomStrategyList } from "./custom-strategy-list";
import { CustomStrategyEditor } from "./custom-strategy-editor";

/** 커스텀 전략 빌더 메인 레이아웃 */
export function CustomStrategyBuilder() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
      {/* 좌측: 전략 목록 */}
      <div className="min-w-0">
        <CustomStrategyList />
      </div>

      {/* 우측: 전략 편집기 */}
      <div className="min-w-0">
        <CustomStrategyEditor />
      </div>
    </div>
  );
}
