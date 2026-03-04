# Sprint 16: 관리자 대시보드 UI + 초대코드 회원가입 플로우 완성

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 백엔드에만 존재하는 관리자 API를 프론트엔드와 연결하여 초대코드 발급, 사용자 승인/비활성화를 UI로 수행할 수 있게 하고, 초대코드 기반 회원가입 플로우를 완성한다.

**Architecture:** 관리자 전용 `/admin` 라우트를 신규 추가하고, 기존 `auth-guard.tsx`를 확장하여 `role=admin` 사용자만 접근 가능하도록 보호한다. 회원가입 페이지(`/register`)는 초대코드 URL 파라미터를 수신하여 자동 입력하는 플로우를 지원한다.

**Tech Stack:** Next.js 16 App Router, TanStack Query, shadcn/ui (Table, Badge, Dialog, Tabs), FastAPI admin.py (기존), JWT auth-store (기존)

---

## 개요

- **스프린트 번호:** Sprint 16
- **브랜치:** sprint-16
- **시작일:** 2026-03-03
- **완료일:** 2026-03-04
- **상태:** 완료

## 목표

Sprint 14에서 구축한 관리자 백엔드 API(`/api/v1/admin/`)를 프론트엔드와 연결하여 실제 사용 가능한 관리자 화면을 완성한다. 또한 초대코드 기반 회원가입 페이지를 완성하여 신규 사용자가 초대링크를 통해 가입할 수 있도록 한다.

### 핵심 목표
1. 관리자 대시보드 UI: 초대코드 발급/목록, 사용자 목록/승인/비활성화
2. 초대코드 링크 복사 기능 (클립보드 + 토스트)
3. 회원가입 페이지 완성 (`/register?code=<초대코드>` URL 파라미터 자동 입력)
4. 관리자 전용 라우트 보호 (role 기반 접근 제어)
5. 백엔드 통합 테스트 추가 (admin API)

## 구현 범위

### 포함 항목 (Must Have)
- `frontend/src/app/admin/` 신규 라우트 (관리자 전용)
- 초대코드 발급/목록 탭 UI (유효기간 선택, 사용 여부 Badge)
- 사용자 목록 테이블 (승인/비활성화 버튼, 상태 Badge)
- role 기반 라우트 보호: `admin-guard.tsx` 또는 기존 `auth-guard.tsx` 확장
- `/register` 페이지: 이메일 + 비밀번호 + 초대코드 입력 폼
- URL 파라미터 `?code=` 자동 주입 (`useSearchParams`)
- 관리자 사이드바 메뉴 항목 추가 (role=admin인 경우에만 표시)
- `backend/tests/api/test_admin.py` 통합 테스트 5개 이상

### 제외 항목 (Out of Scope)
- 사용자별 사용량 통계/모니터링 차트 (향후 Phase)
- 비밀번호 재설정 이메일 발송 (SMTP 미설정)
- 역할 변경 (admin ↔ user) UI (보안 위험, 향후 검토)
- Celery 기반 작업 큐 도입 (별도 스프린트)

## 기술적 접근 방법

### 관리자 라우트 보호
```
middleware.ts (기존) → 로그인 여부 체크
auth-guard.tsx (기존) → 인증 후 리다이렉트
admin-guard.tsx (신규) → role !== 'admin' 시 /dashboard 리다이렉트
```

### API 클라이언트 타입 추가
```typescript
// frontend/src/lib/api/types.ts 에 추가
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
```

### 프론트엔드 훅 구조
```
hooks/use-admin.ts
  - useInvitations()        → GET /api/v1/admin/invitations
  - useCreateInvitation()   → POST /api/v1/admin/invitations
  - useUsers()              → GET /api/v1/admin/users
  - useApproveUser()        → PUT /api/v1/admin/users/{id}/approve
  - useDeactivateUser()     → PUT /api/v1/admin/users/{id}/deactivate
```

### 회원가입 플로우
```
/register?code=abc123
  → RegisterPage
    → useSearchParams() → code 자동 입력
    → POST /auth/register { username, email, password, invitation_code }
    → 성공 → /login 리다이렉트 + "가입 완료, 관리자 승인 대기" 토스트
```

## 의존성 및 리스크

| 항목 | 내용 |
|------|------|
| 의존성 | Sprint 14 JWT 인증 완료 (완료), admin.py API 완료 (완료) |
| 리스크 1 | auth-store에 role 정보 없을 경우 → JWT 디코딩 또는 /auth/me 엔드포인트 필요 |
| 리스크 2 | 관리자 자기 자신 비활성화 방지 → 백엔드에서 이미 400 처리, 프론트에서도 버튼 비활성화 |
| 리스크 3 | 초대코드 URL 노출 → HTTPS 환경에서만 공유, 만료 기간 설정으로 완화 |

## 완료 기준 (Definition of Done)

- ✅ `/admin` 페이지: 초대코드 탭, 사용자 탭 모두 정상 렌더링
- ✅ 초대코드 생성 → 목록 반영 → 클립보드 복사 동작
- ✅ 사용자 목록 조회 → 승인/비활성화 버튼 동작
- ✅ `/register?code=abc` 접속 시 초대코드 자동 입력
- ✅ 회원가입 성공 → /login으로 이동 + 성공 토스트
- ✅ 비관리자 사용자가 `/admin` 접속 시 `/dashboard`로 리다이렉트
- ✅ 사이드바에서 관리자 계정에게만 "관리자" 메뉴 표시
- ✅ `test_admin.py` 통합 테스트 5개 이상 PASSED
- ✅ 전체 기존 테스트(45개) 회귀 없음

## 예상 산출물

- `frontend/src/app/admin/page.tsx` (관리자 대시보드)
- `frontend/src/app/register/page.tsx` (회원가입 페이지)
- `frontend/src/hooks/use-admin.ts` (관리자 API 훅)
- `frontend/src/components/admin/invitation-tab.tsx`
- `frontend/src/components/admin/user-tab.tsx`
- `frontend/src/components/layout/admin-guard.tsx`
- `backend/tests/api/test_admin.py` (통합 테스트)

---

## Task 0: 브랜치 생성

**Files:**
- 없음 (Git 명령만 수행)

**Step 1: 브랜치 생성**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git checkout main
git pull origin main
git checkout -b sprint-16
```

Expected: `sprint-16` 브랜치로 전환됨

**Step 2: 확인**

```bash
git branch --show-current
```

Expected: `sprint-16`

---

## Task 1: 백엔드 관리자 API 통합 테스트

> 기존 admin.py API를 검증하는 테스트를 먼저 작성한다. TDD 원칙에 따라 테스트 → 구현 확인 순서로 진행.

**Files:**
- Create: `backend/tests/api/test_admin.py`

**Step 1: 테스트 파일 작성**

```python
"""
관리자 API 통합 테스트
GET    /api/v1/admin/invitations
POST   /api/v1/admin/invitations
GET    /api/v1/admin/users
PUT    /api/v1/admin/users/{id}/approve
PUT    /api/v1/admin/users/{id}/deactivate
"""
import pytest

from app.models.invitation import InvitationCode
from app.models.user import ROLE_ADMIN, ROLE_USER, User


@pytest.mark.asyncio
async def test_non_admin_cannot_list_invitations(client_with_user):
    """일반 사용자는 초대코드 목록 조회 불가 (403)"""
    response = await client_with_user.get("/api/v1/admin/invitations")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_invitations(client_with_admin):
    """관리자는 초대코드 목록 조회 가능"""
    response = await client_with_admin.get("/api/v1/admin/invitations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_admin_can_create_invitation(client_with_admin):
    """관리자가 초대코드 생성"""
    response = await client_with_admin.post(
        "/api/v1/admin/invitations",
        json={"expires_days": 7},
    )
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert data["is_used"] is False
    assert len(data["code"]) > 10  # token_urlsafe(16) 길이 확인


@pytest.mark.asyncio
async def test_admin_can_list_users(client_with_admin):
    """관리자는 사용자 목록 조회 가능"""
    response = await client_with_admin.get("/api/v1/admin/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1  # 관리자 자신 포함


@pytest.mark.asyncio
async def test_admin_can_approve_user(client_with_admin, db_session):
    """관리자가 일반 사용자 승인"""
    import bcrypt
    pw_hash = bcrypt.hashpw(b"testpass", bcrypt.gensalt()).decode()
    new_user = User(
        username="pending_user",
        email="pending@example.com",
        password_hash=pw_hash,
        role=ROLE_USER,
        is_approved=False,
        is_active=True,
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    response = await client_with_admin.put(
        f"/api/v1/admin/users/{new_user.id}/approve"
    )
    assert response.status_code == 200
    assert response.json()["is_approved"] is True


@pytest.mark.asyncio
async def test_admin_cannot_deactivate_self(client_with_admin, admin_user):
    """관리자는 자기 자신을 비활성화할 수 없음 (400)"""
    response = await client_with_admin.put(
        f"/api/v1/admin/users/{admin_user.id}/deactivate"
    )
    assert response.status_code == 400
```

**Step 2: conftest.py에 `client_with_admin`, `admin_user` 픽스처 추가**

> `backend/tests/conftest.py`를 읽고 기존 `client_with_user` 패턴을 참고하여 동일한 구조로 추가.

```python
# conftest.py 추가 픽스처
@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """테스트용 관리자 사용자 픽스처"""
    import bcrypt
    pw_hash = bcrypt.hashpw(b"adminpass", bcrypt.gensalt()).decode()
    user = User(
        username="admin_test",
        email="admin_test@example.com",
        password_hash=pw_hash,
        role=ROLE_ADMIN,
        is_approved=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def client_with_admin(client: AsyncClient, admin_user: User) -> AsyncClient:
    """관리자 JWT 토큰이 주입된 테스트 클라이언트"""
    from app.core.auth import create_access_token
    token = create_access_token({"sub": str(admin_user.id)})
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

**Step 3: 테스트 실행 (실패 확인)**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/backend
python -m pytest tests/api/test_admin.py -v
```

Expected: conftest에 admin 픽스처 없으면 FAIL, 있으면 PASS

**Step 4: conftest.py 수정 후 재실행**

```bash
python -m pytest tests/api/test_admin.py -v
```

Expected: `6 passed`

**Step 5: 전체 테스트 회귀 확인**

```bash
python -m pytest tests/ -v --tb=short 2>&1 | tail -5
```

Expected: 기존 45개 + 신규 6개 = `51 passed` 이상

**Step 6: 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add backend/tests/api/test_admin.py backend/tests/conftest.py
git commit -m "test: 관리자 API 통합 테스트 추가 (6개)"
```

---

## Task 2: auth-store role 필드 확인 + /auth/me 엔드포인트

> 프론트엔드에서 현재 사용자의 role을 알아야 관리자 메뉴를 조건부로 렌더링할 수 있다.
> 현재 auth-store에 role이 저장되는지 확인하고, 없으면 `/auth/me` 엔드포인트를 추가한다.

**Files:**
- Read: `frontend/src/stores/auth-store.ts`
- Read: `backend/app/api/v1/auth.py`
- Modify (조건부): `backend/app/api/v1/auth.py`
- Modify (조건부): `frontend/src/stores/auth-store.ts`

**Step 1: auth-store.ts 현재 상태 확인**

```bash
cat /Users/choijiseon/Documents/Sources/mystock.bot/frontend/src/stores/auth-store.ts
```

- `role` 필드가 이미 저장되는 경우: Task 2 스킵, Task 3으로 이동
- `role` 필드 없는 경우: 아래 Step 2~5 수행

**Step 2: 백엔드 /auth/me 엔드포인트 추가**

`backend/app/api/v1/auth.py` 파일에 아래 엔드포인트 추가:

```python
class MeResponse(BaseModel):
    """현재 사용자 정보 응답"""
    id: int
    username: str
    email: str | None
    role: str
    is_approved: bool

    model_config = {"from_attributes": True}


@router.get("/me", response_model=MeResponse, summary="현재 사용자 정보")
async def get_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자의 정보를 반환한다."""
    return current_user
```

**Step 3: auth-store.ts에 role 필드 추가**

```typescript
// stores/auth-store.ts 수정 — role, userId 필드 추가
interface AuthState {
  token: string | null;
  refreshToken: string | null;
  role: string | null;       // 추가
  userId: number | null;      // 추가
  setToken: (token: string, refreshToken: string) => void;
  setRole: (role: string, userId: number) => void;  // 추가
  clearAuth: () => void;
}
```

**Step 4: 로그인 응답에서 role 저장**

`frontend/src/app/login/page.tsx` 또는 로그인 훅에서 로그인 성공 후 `/auth/me` 호출하여 role 저장:

```typescript
// 로그인 성공 후
const me = await apiClient.get('/auth/me');
useAuthStore.getState().setRole(me.role, me.id);
```

**Step 5: 커밋**

```bash
git add backend/app/api/v1/auth.py frontend/src/stores/auth-store.ts frontend/src/app/login/page.tsx
git commit -m "feat: /auth/me 엔드포인트 추가 및 auth-store role 저장"
```

---

## Task 3: 관리자 API 훅 작성 (프론트엔드)

**Files:**
- Create: `frontend/src/hooks/use-admin.ts`
- Modify: `frontend/src/lib/api/types.ts`

**Step 1: types.ts에 관리자 타입 추가**

`frontend/src/lib/api/types.ts` 파일 끝에 추가:

```typescript
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
```

**Step 2: use-admin.ts 작성**

```typescript
// frontend/src/hooks/use-admin.ts
"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import type { AdminInvitation, AdminUser, CreateInvitationRequest } from "@/lib/api/types";

// 쿼리 키
const QUERY_KEYS = {
  invitations: ["admin", "invitations"] as const,
  users: ["admin", "users"] as const,
};

// 초대코드 목록 조회
export function useInvitations() {
  return useQuery<AdminInvitation[]>({
    queryKey: QUERY_KEYS.invitations,
    queryFn: async () => {
      const res = await apiClient.get("/admin/invitations");
      if (!res.ok) throw new Error("초대코드 목록 조회 실패");
      return res.json();
    },
    staleTime: 1000 * 30, // 30초 캐시
  });
}

// 초대코드 생성
export function useCreateInvitation() {
  const queryClient = useQueryClient();
  return useMutation<AdminInvitation, Error, CreateInvitationRequest>({
    mutationFn: async (body) => {
      const res = await apiClient.post("/admin/invitations", body);
      if (!res.ok) throw new Error("초대코드 생성 실패");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.invitations });
      toast.success("초대코드가 생성되었습니다.");
    },
  });
}

// 사용자 목록 조회
export function useAdminUsers() {
  return useQuery<AdminUser[]>({
    queryKey: QUERY_KEYS.users,
    queryFn: async () => {
      const res = await apiClient.get("/admin/users");
      if (!res.ok) throw new Error("사용자 목록 조회 실패");
      return res.json();
    },
    staleTime: 1000 * 30,
  });
}

// 사용자 승인
export function useApproveUser() {
  const queryClient = useQueryClient();
  return useMutation<AdminUser, Error, number>({
    mutationFn: async (userId) => {
      const res = await apiClient.put(`/admin/users/${userId}/approve`);
      if (!res.ok) throw new Error("사용자 승인 실패");
      return res.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.users });
      toast.success(`${data.username} 사용자를 승인했습니다.`);
    },
  });
}

// 사용자 비활성화
export function useDeactivateUser() {
  const queryClient = useQueryClient();
  return useMutation<AdminUser, Error, number>({
    mutationFn: async (userId) => {
      const res = await apiClient.put(`/admin/users/${userId}/deactivate`);
      if (!res.ok) throw new Error("사용자 비활성화 실패");
      return res.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.users });
      toast.success(`${data.username} 사용자를 비활성화했습니다.`);
    },
  });
}
```

**Step 3: TypeScript 타입 검사**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx tsc --noEmit 2>&1 | head -20
```

Expected: 에러 없음

**Step 4: 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add frontend/src/hooks/use-admin.ts frontend/src/lib/api/types.ts
git commit -m "feat: 관리자 API 훅 추가 (useInvitations, useAdminUsers, useApproveUser, useDeactivateUser)"
```

---

## Task 4: AdminGuard 컴포넌트 (관리자 전용 라우트 보호)

**Files:**
- Create: `frontend/src/components/layout/admin-guard.tsx`

**Step 1: admin-guard.tsx 작성**

```typescript
// frontend/src/components/layout/admin-guard.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

interface AdminGuardProps {
  children: React.ReactNode;
}

/**
 * 관리자 전용 라우트 보호 컴포넌트
 * role !== 'admin' 인 경우 /dashboard 로 리다이렉트한다.
 */
export function AdminGuard({ children }: AdminGuardProps) {
  const router = useRouter();
  const role = useAuthStore((state) => state.role);
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    // 토큰 없으면 로그인 페이지로
    if (!token) {
      router.replace("/login");
      return;
    }
    // role이 로드되었는데 admin이 아니면 대시보드로
    if (role !== null && role !== "admin") {
      router.replace("/dashboard");
    }
  }, [role, token, router]);

  // role 로딩 중 또는 admin인 경우 렌더링
  if (!token || (role !== null && role !== "admin")) {
    return null;
  }

  return <>{children}</>;
}
```

**Step 2: TypeScript 타입 검사**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx tsc --noEmit 2>&1 | head -20
```

Expected: 에러 없음

**Step 3: 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add frontend/src/components/layout/admin-guard.tsx
git commit -m "feat: AdminGuard 컴포넌트 추가 (관리자 전용 라우트 보호)"
```

---

## Task 5: 초대코드 탭 컴포넌트

**Files:**
- Create: `frontend/src/components/admin/invitation-tab.tsx`

**Step 1: invitation-tab.tsx 작성**

```typescript
// frontend/src/components/admin/invitation-tab.tsx
"use client";

import { useState } from "react";
import { Copy, Plus, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCreateInvitation, useInvitations } from "@/hooks/use-admin";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function isExpired(expiresAt: string): boolean {
  return new Date(expiresAt) < new Date();
}

export function InvitationTab() {
  const { data: invitations, isLoading, refetch } = useInvitations();
  const createMutation = useCreateInvitation();
  const [expiresDays, setExpiresDays] = useState("7");

  const handleCreate = () => {
    createMutation.mutate({ expires_days: parseInt(expiresDays) });
  };

  const handleCopyLink = (code: string) => {
    const url = `${window.location.origin}/register?code=${code}`;
    navigator.clipboard.writeText(url).then(() => {
      toast.success("초대 링크가 클립보드에 복사되었습니다.");
    });
  };

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code).then(() => {
      toast.success("초대코드가 복사되었습니다.");
    });
  };

  return (
    <div className="space-y-4">
      {/* 생성 영역 */}
      <div className="flex items-center gap-3">
        <Select value={expiresDays} onValueChange={setExpiresDays}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="유효기간" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1">1일</SelectItem>
            <SelectItem value="3">3일</SelectItem>
            <SelectItem value="7">7일</SelectItem>
            <SelectItem value="30">30일</SelectItem>
          </SelectContent>
        </Select>
        <Button
          onClick={handleCreate}
          disabled={createMutation.isPending}
          size="sm"
        >
          <Plus className="h-4 w-4 mr-1" />
          초대코드 생성
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
        </Button>
      </div>

      {/* 목록 테이블 */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>코드</TableHead>
            <TableHead>상태</TableHead>
            <TableHead>만료일</TableHead>
            <TableHead className="text-right">액션</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={4} className="text-center text-muted-foreground">
                로딩 중...
              </TableCell>
            </TableRow>
          ) : invitations?.length === 0 ? (
            <TableRow>
              <TableCell colSpan={4} className="text-center text-muted-foreground">
                초대코드가 없습니다.
              </TableCell>
            </TableRow>
          ) : (
            invitations?.map((inv) => (
              <TableRow key={inv.id}>
                <TableCell className="font-mono text-sm">{inv.code}</TableCell>
                <TableCell>
                  {inv.is_used ? (
                    <Badge variant="secondary">사용됨</Badge>
                  ) : isExpired(inv.expires_at) ? (
                    <Badge variant="destructive">만료됨</Badge>
                  ) : (
                    <Badge variant="default">유효</Badge>
                  )}
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDate(inv.expires_at)}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopyCode(inv.code)}
                      disabled={inv.is_used || isExpired(inv.expires_at)}
                    >
                      <Copy className="h-3 w-3 mr-1" />
                      코드 복사
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopyLink(inv.code)}
                      disabled={inv.is_used || isExpired(inv.expires_at)}
                    >
                      <Copy className="h-3 w-3 mr-1" />
                      링크 복사
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
```

**Step 2: 필요한 shadcn/ui 컴포넌트 설치 확인**

```bash
ls /Users/choijiseon/Documents/Sources/mystock.bot/frontend/src/components/ui/ | grep -E "table|select|badge"
```

없으면 설치:
```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx shadcn@latest add table select badge --yes 2>/dev/null || true
```

**Step 3: TypeScript 타입 검사**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx tsc --noEmit 2>&1 | head -20
```

**Step 4: 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add frontend/src/components/admin/invitation-tab.tsx
git commit -m "feat: 관리자 초대코드 탭 컴포넌트 추가"
```

---

## Task 6: 사용자 관리 탭 컴포넌트

**Files:**
- Create: `frontend/src/components/admin/user-tab.tsx`

**Step 1: user-tab.tsx 작성**

```typescript
// frontend/src/components/admin/user-tab.tsx
"use client";

import { RefreshCw, ShieldCheck, UserX } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAdminUsers, useApproveUser, useDeactivateUser } from "@/hooks/use-admin";
import { useAuthStore } from "@/stores/auth-store";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

export function UserTab() {
  const { data: users, isLoading, refetch } = useAdminUsers();
  const approveMutation = useApproveUser();
  const deactivateMutation = useDeactivateUser();
  const currentUserId = useAuthStore((state) => state.userId);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <span className="text-sm text-muted-foreground">
          총 {users?.length ?? 0}명의 사용자
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
        </Button>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>사용자명</TableHead>
            <TableHead>이메일</TableHead>
            <TableHead>역할</TableHead>
            <TableHead>승인</TableHead>
            <TableHead>활성</TableHead>
            <TableHead>가입일</TableHead>
            <TableHead className="text-right">액션</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                로딩 중...
              </TableCell>
            </TableRow>
          ) : users?.length === 0 ? (
            <TableRow>
              <TableCell colSpan={8} className="text-center text-muted-foreground">
                사용자가 없습니다.
              </TableCell>
            </TableRow>
          ) : (
            users?.map((user) => (
              <TableRow key={user.id}>
                <TableCell className="text-sm">{user.id}</TableCell>
                <TableCell className="font-medium">{user.username}</TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {user.email ?? "-"}
                </TableCell>
                <TableCell>
                  {user.role === "admin" ? (
                    <Badge variant="default">관리자</Badge>
                  ) : (
                    <Badge variant="outline">일반</Badge>
                  )}
                </TableCell>
                <TableCell>
                  {user.is_approved ? (
                    <Badge variant="default" className="bg-green-600">승인됨</Badge>
                  ) : (
                    <Badge variant="secondary">대기</Badge>
                  )}
                </TableCell>
                <TableCell>
                  {user.is_active ? (
                    <Badge variant="outline">활성</Badge>
                  ) : (
                    <Badge variant="destructive">비활성</Badge>
                  )}
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDate(user.created_at)}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    {!user.is_approved && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => approveMutation.mutate(user.id)}
                        disabled={approveMutation.isPending}
                      >
                        <ShieldCheck className="h-3 w-3 mr-1" />
                        승인
                      </Button>
                    )}
                    {user.is_active && user.id !== currentUserId && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => deactivateMutation.mutate(user.id)}
                        disabled={deactivateMutation.isPending}
                      >
                        <UserX className="h-3 w-3 mr-1" />
                        비활성화
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
```

**Step 2: TypeScript 타입 검사**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx tsc --noEmit 2>&1 | head -20
```

**Step 3: 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add frontend/src/components/admin/user-tab.tsx
git commit -m "feat: 관리자 사용자 관리 탭 컴포넌트 추가"
```

---

## Task 7: 관리자 대시보드 페이지 조립

**Files:**
- Create: `frontend/src/app/admin/page.tsx`

**Step 1: admin/page.tsx 작성**

```typescript
// frontend/src/app/admin/page.tsx
"use client";

import { Shield } from "lucide-react";
import { AdminGuard } from "@/components/layout/admin-guard";
import { InvitationTab } from "@/components/admin/invitation-tab";
import { UserTab } from "@/components/admin/user-tab";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function AdminPage() {
  return (
    <AdminGuard>
      <div className="p-6 space-y-6">
        {/* 헤더 */}
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          <h1 className="text-2xl font-bold">관리자 대시보드</h1>
        </div>

        {/* 탭 */}
        <Tabs defaultValue="invitations">
          <TabsList>
            <TabsTrigger value="invitations">초대코드 관리</TabsTrigger>
            <TabsTrigger value="users">사용자 관리</TabsTrigger>
          </TabsList>
          <TabsContent value="invitations" className="mt-4">
            <InvitationTab />
          </TabsContent>
          <TabsContent value="users" className="mt-4">
            <UserTab />
          </TabsContent>
        </Tabs>
      </div>
    </AdminGuard>
  );
}
```

**Step 2: TypeScript 타입 검사**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx tsc --noEmit 2>&1 | head -20
```

Expected: 에러 없음

**Step 3: 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add frontend/src/app/admin/page.tsx
git commit -m "feat: 관리자 대시보드 페이지 추가 (/admin)"
```

---

## Task 8: 사이드바에 관리자 메뉴 추가 (role 조건부 표시)

**Files:**
- Modify: `frontend/src/components/layout/app-sidebar.tsx`

**Step 1: app-sidebar.tsx 수정**

기존 `navItems` 배열은 그대로 두고, 관리자 전용 항목을 role 조건부로 렌더링:

```typescript
// 상단에 import 추가
import { Shield } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";

// SidebarContent 함수 내부에 추가
const role = useAuthStore((state) => state.role);

// 기존 navItems map 이후, nav 닫기 태그 전에 추가
{role === "admin" && (
  <>
    <div className="mx-3 my-2 border-t" />
    <Link
      href="/admin"
      onClick={close}
      className={cn(
        "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
        pathname === "/admin"
          ? "bg-primary text-primary-foreground"
          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
      )}
    >
      <Shield className="h-4 w-4 shrink-0" />
      관리자
    </Link>
  </>
)}
```

**Step 2: TypeScript 타입 검사**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx tsc --noEmit 2>&1 | head -20
```

**Step 3: 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add frontend/src/components/layout/app-sidebar.tsx
git commit -m "feat: 사이드바에 관리자 메뉴 추가 (role=admin 조건부)"
```

---

## Task 9: 회원가입 페이지 구현

> `/register?code=<초대코드>` URL 파라미터를 자동으로 읽어 초대코드 입력란에 채워주는 페이지.

**Files:**
- Create: `frontend/src/app/register/page.tsx`

**Step 1: register/page.tsx 작성**

```typescript
// frontend/src/app/register/page.tsx
"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiClient } from "@/lib/api/client";

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialCode = searchParams.get("code") ?? "";

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    invitationCode: initialCode,
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (form.password !== form.confirmPassword) {
      toast.error("비밀번호가 일치하지 않습니다.");
      return;
    }
    if (form.password.length < 8) {
      toast.error("비밀번호는 8자 이상이어야 합니다.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await apiClient.post("/auth/register", {
        username: form.username,
        email: form.email,
        password: form.password,
        invitation_code: form.invitationCode,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? "회원가입에 실패했습니다.");
      }
      toast.success("회원가입이 완료되었습니다. 관리자 승인 후 로그인 가능합니다.");
      router.push("/login");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "회원가입에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>회원가입</CardTitle>
          <CardDescription>
            초대코드를 통해 AutoTrader KR에 가입합니다.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">사용자명</Label>
              <Input
                id="username"
                placeholder="사용자명 (영문, 숫자)"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
                minLength={2}
                maxLength={50}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">이메일</Label>
              <Input
                id="email"
                type="email"
                placeholder="이메일 주소"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">비밀번호</Label>
              <Input
                id="password"
                type="password"
                placeholder="8자 이상"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
                minLength={8}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">비밀번호 확인</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="비밀번호 재입력"
                value={form.confirmPassword}
                onChange={(e) =>
                  setForm({ ...form, confirmPassword: e.target.value })
                }
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invitationCode">초대코드</Label>
              <Input
                id="invitationCode"
                placeholder="초대코드 입력"
                value={form.invitationCode}
                onChange={(e) =>
                  setForm({ ...form, invitationCode: e.target.value })
                }
                required
              />
              {initialCode && (
                <p className="text-xs text-muted-foreground">
                  초대링크에서 자동으로 입력되었습니다.
                </p>
              )}
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "가입 중..." : "회원가입"}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              이미 계정이 있으신가요?{" "}
              <Link href="/login" className="underline">
                로그인
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

// useSearchParams는 Suspense로 감싸야 함 (Next.js App Router 요구사항)
export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">로딩 중...</div>}>
      <RegisterForm />
    </Suspense>
  );
}
```

**Step 2: middleware.ts에서 /register 경로 공개 처리**

`frontend/src/middleware.ts` 파일을 읽고 `/register`가 공개 경로인지 확인:

```bash
cat /Users/choijiseon/Documents/Sources/mystock.bot/frontend/src/middleware.ts
```

`/register`가 publicPaths에 없으면 추가:
```typescript
const publicPaths = ["/login", "/register"]; // /register 추가
```

**Step 3: TypeScript 타입 검사**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx tsc --noEmit 2>&1 | head -20
```

**Step 4: 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add frontend/src/app/register/page.tsx frontend/src/middleware.ts
git commit -m "feat: 초대코드 기반 회원가입 페이지 추가 (/register)"
```

---

## Task 10: Playwright E2E 검증

> Docker 환경에서 전체 플로우를 브라우저로 검증한다.

**사전 조건:** `docker compose up -d` 실행 후 `http://localhost:3001` 접속 가능 상태

**검증 시나리오 1: 관리자 로그인 후 /admin 접속**

```
1. browser_navigate -> http://localhost:3001/login
2. browser_fill_form -> 이메일: frogy95@gmail.com, 비밀번호: 관리자 비밀번호
3. browser_click -> 로그인 버튼
4. browser_wait_for -> /dashboard 리다이렉트 확인
5. browser_navigate -> http://localhost:3001/admin
6. browser_snapshot -> 관리자 대시보드 렌더링 확인 (초대코드 탭, 사용자 탭)
7. browser_console_messages(level: "error") -> 에러 없음 확인
```

**검증 시나리오 2: 초대코드 생성 및 링크 복사**

```
1. browser_navigate -> http://localhost:3001/admin (관리자 로그인 상태)
2. browser_snapshot -> 초대코드 탭 확인
3. browser_click -> "초대코드 생성" 버튼
4. browser_wait_for -> 새 행이 테이블에 추가됨
5. browser_snapshot -> 생성된 초대코드 행 확인
6. browser_network_requests -> POST /api/v1/admin/invitations 200 확인
```

**검증 시나리오 3: 비관리자가 /admin 접속 시 리다이렉트**

```
1. 데모 모드로 로그인 (일반 유저)
2. browser_navigate -> http://localhost:3001/admin
3. browser_wait_for -> /dashboard 리다이렉트 확인
4. browser_snapshot -> 대시보드 페이지 표시 확인
```

**검증 시나리오 4: 회원가입 페이지**

```
1. browser_navigate -> http://localhost:3001/register?code=test123
2. browser_snapshot -> 폼 렌더링 확인, 초대코드 입력란에 "test123" 자동 입력 확인
3. browser_console_messages(level: "error") -> 에러 없음 확인
```

**검증 시나리오 5: 사이드바 관리자 메뉴 표시**

```
1. 관리자 로그인 후
2. browser_snapshot -> 사이드바에 "관리자" 메뉴 항목 표시 확인
3. 데모 모드(일반 유저) 로그인 후
4. browser_snapshot -> 사이드바에 "관리자" 메뉴 없음 확인
```

---

## Task 11: 전체 테스트 검증 및 마무리

**Step 1: 전체 백엔드 테스트 실행**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/backend
python -m pytest tests/ -v --tb=short 2>&1 | tail -10
```

Expected: `51 passed` 이상 (기존 45 + 신규 6)

**Step 2: 프론트엔드 빌드 검사**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot/frontend
npx tsc --noEmit 2>&1
```

Expected: 에러 없음

**Step 3: ROADMAP.md Sprint 16 항목 추가**

ROADMAP.md의 부록 스프린트 캘린더 테이블에 Sprint 16 행 추가:
```
| Sprint 16 | 2026-03-03 | Phase 8 | 관리자 대시보드 UI + 초대코드 회원가입 플로우 완성 |
```

ROADMAP.md 현황 대시보드의 `현재 진행 단계` 업데이트:
```
Phase 8 진행 중 — Sprint 16: 관리자 대시보드 UI
```

**Step 4: 최종 커밋**

```bash
cd /Users/choijiseon/Documents/Sources/mystock.bot
git add ROADMAP.md
git commit -m "docs: ROADMAP.md Sprint 16 항목 추가"
```

---

## 예상 산출물 요약

| 파일 | 유형 | 설명 |
|------|------|------|
| `frontend/src/app/admin/page.tsx` | 신규 | 관리자 대시보드 페이지 |
| `frontend/src/app/register/page.tsx` | 신규 | 초대코드 회원가입 페이지 |
| `frontend/src/hooks/use-admin.ts` | 신규 | 관리자 API TanStack Query 훅 |
| `frontend/src/components/admin/invitation-tab.tsx` | 신규 | 초대코드 관리 탭 |
| `frontend/src/components/admin/user-tab.tsx` | 신규 | 사용자 관리 탭 |
| `frontend/src/components/layout/admin-guard.tsx` | 신규 | 관리자 라우트 보호 컴포넌트 |
| `frontend/src/lib/api/types.ts` | 수정 | AdminInvitation, AdminUser 타입 추가 |
| `frontend/src/components/layout/app-sidebar.tsx` | 수정 | 관리자 메뉴 조건부 추가 |
| `frontend/src/middleware.ts` | 수정 | /register 공개 경로 추가 |
| `backend/app/api/v1/auth.py` | 수정 | GET /auth/me 엔드포인트 추가 |
| `backend/tests/api/test_admin.py` | 신규 | 관리자 API 통합 테스트 6개 |
| `backend/tests/conftest.py` | 수정 | admin_user, client_with_admin 픽스처 추가 |

## Playwright MCP 검증 시나리오 요약

| 시나리오 | 검증 내용 |
|----------|----------|
| TC-1 | 관리자 로그인 → /admin 접속 → 탭 렌더링 |
| TC-2 | 초대코드 생성 → 목록 반영 → API 200 |
| TC-3 | 비관리자 /admin 접속 → /dashboard 리다이렉트 |
| TC-4 | /register?code=abc → 초대코드 자동 입력 |
| TC-5 | 관리자 사이드바에 "관리자" 메뉴 조건부 표시 |
