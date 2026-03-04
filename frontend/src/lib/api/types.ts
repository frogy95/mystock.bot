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

// ===== 관리자 API 타입 =====

export interface AdminInvitation {
  id: number;
  code: string;
  created_by: number;
  used_by: number | null;
  expires_at: string;
  is_used: boolean;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string | null;
  role: string;
  is_approved: boolean;
  is_active: boolean;
  created_at: string;
}

export interface CreateInvitationRequest {
  expires_days: number;
}
