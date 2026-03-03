/** 백엔드 주문 응답 타입 (공용) */
export interface OrderAPI {
  id: number;
  stock_code: string;
  order_type: string;      // "buy" | "sell"
  status: string;          // "pending" | "filled" | "cancelled" | "failed" | "simulated"
  strategy_id: number | null;
  quantity: number | null;
  price: number | null;
  created_at: string;
  updated_at: string;
}
