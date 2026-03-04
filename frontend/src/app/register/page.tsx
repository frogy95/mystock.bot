"use client";

/**
 * 회원가입 페이지
 * 초대코드 기반 회원가입 폼 — URL 파라미터 ?code= 자동 읽기
 */
import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Bot } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiClient } from "@/lib/api/client";

/** 회원가입 폼 — useSearchParams 사용으로 Suspense 내부에서 렌더링 */
function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    passwordConfirm: "",
    invitationCode: searchParams.get("code") ?? "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (form.password !== form.passwordConfirm) {
      toast.error("비밀번호가 일치하지 않습니다.");
      return;
    }

    setLoading(true);
    try {
      await apiClient.post("/api/v1/auth/register", {
        username: form.username,
        email: form.email,
        password: form.password,
        invitation_code: form.invitationCode,
      });
      toast.success("회원가입이 완료되었습니다. 관리자 승인 후 로그인 가능합니다.");
      router.push("/login");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "회원가입에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <div className="flex items-center gap-2 mb-1">
            <Bot className="h-5 w-5 text-primary" />
            <span className="font-semibold text-primary">mystock.bot</span>
          </div>
          <CardTitle className="text-xl">회원가입</CardTitle>
          <p className="text-sm text-muted-foreground">
            초대코드가 있는 경우 아래 폼을 작성해주세요.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="username">사용자명</Label>
              <Input
                id="username"
                name="username"
                value={form.username}
                onChange={handleChange}
                placeholder="사용자명 입력"
                autoComplete="username"
                disabled={loading}
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">이메일</Label>
              <Input
                id="email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                placeholder="이메일 입력"
                autoComplete="email"
                disabled={loading}
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">비밀번호</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                placeholder="비밀번호 입력"
                autoComplete="new-password"
                disabled={loading}
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="passwordConfirm">비밀번호 확인</Label>
              <Input
                id="passwordConfirm"
                name="passwordConfirm"
                type="password"
                value={form.passwordConfirm}
                onChange={handleChange}
                placeholder="비밀번호 재입력"
                autoComplete="new-password"
                disabled={loading}
                required
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="invitationCode">초대코드</Label>
              <Input
                id="invitationCode"
                name="invitationCode"
                value={form.invitationCode}
                onChange={handleChange}
                placeholder="초대코드 입력"
                disabled={loading}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "처리 중..." : "회원가입"}
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              이미 계정이 있으신가요?{" "}
              <a href="/login" className="text-primary underline underline-offset-4">
                로그인
              </a>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

/** 회원가입 페이지 — useSearchParams 사용 시 Suspense 필수 */
export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">로딩 중...</div>}>
      <RegisterForm />
    </Suspense>
  );
}
