/** 금액을 한국 원화 형식으로 포맷 (예: 1,234,567원) */
export function formatKRW(value: number): string {
  return new Intl.NumberFormat("ko-KR").format(value) + "원";
}

/** 금액을 축약 형식으로 포맷 (예: 1.2억, 5,340만) */
export function formatKRWCompact(value: number): string {
  if (Math.abs(value) >= 100_000_000) {
    return (value / 100_000_000).toFixed(1) + "억";
  }
  if (Math.abs(value) >= 10_000) {
    return new Intl.NumberFormat("ko-KR").format(Math.round(value / 10_000)) + "만";
  }
  return new Intl.NumberFormat("ko-KR").format(value);
}

/** 수익률 포맷 (예: +3.47%, -1.22%) */
export function formatPercent(value: number): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

/** 등락금액 포맷 (예: +900, -800) */
export function formatChange(value: number): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${new Intl.NumberFormat("ko-KR").format(value)}`;
}

/** 거래량 축약 포맷 (예: 1,234만) */
export function formatVolume(value: number): string {
  if (value >= 100_000_000) {
    return (value / 100_000_000).toFixed(1) + "억";
  }
  if (value >= 10_000) {
    return new Intl.NumberFormat("ko-KR").format(Math.round(value / 10_000)) + "만";
  }
  return new Intl.NumberFormat("ko-KR").format(value);
}

/** 날짜/시간 포맷 (예: 03/01 09:32) */
export function formatDateTime(isoString: string): string {
  const date = new Date(isoString);
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${month}/${day} ${hours}:${minutes}`;
}

/** 시각 포맷 (예: 09:32) */
export function formatTime(isoString: string): string {
  const date = new Date(isoString);
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

/** 날짜 문자열을 한국 날짜 형식으로 포맷 (예: "2026-03-01" → "2026.03.01") */
export function formatDate(dateString: string): string {
  return dateString.replace(/-/g, ".");
}

/** ISO 날짜 시간을 연도 포함 한국 날짜+시간 형식으로 포맷 (예: "2026-03-01T09:32:00Z" → "2026.03.01 09:32") */
export function formatDateTimeFull(isoString: string): string {
  const date = new Date(isoString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${year}.${month}.${day} ${hours}:${minutes}`;
}
