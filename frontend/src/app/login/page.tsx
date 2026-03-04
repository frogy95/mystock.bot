"use client";

/**
 * 로그인 페이지
 * 좌우 분할 레이아웃: 왼쪽 브랜딩 + 오른쪽 로그인 폼
 */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, Cpu, Shield, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/stores/auth-store";
import { apiClient } from "@/lib/api/client";

const FEATURES = [
  { icon: TrendingUp, label: "실시간 시세", desc: "KIS API 기반 실시간 주가 조회" },
  { icon: Cpu, label: "AI 전략", desc: "골든크로스, 볼린저 밴드 등 자동 전략" },
  { icon: Bot, label: "자동매매", desc: "신호 감지 후 자동 주문 실행" },
  { icon: Shield, label: "안전장치", desc: "일일 손실 한도 및 긴급 매도 제어" },
];

interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);
  const setRole = useAuthStore((state) => state.setRole);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await apiClient.post<TokenResponse>("/api/v1/auth/login", {
        email,
        password,
      });
      // JWT 페이로드에서 username 추출 (또는 email을 username으로 사용)
      const username = email.split("@")[0];
      login(data.access_token, username, data.refresh_token);
      // /auth/me 호출로 role과 userId를 저장한다
      try {
        const me = await apiClient.get<{
          id: number;
          username: string;
          email: string | null;
          role: string;
          is_approved: boolean;
        }>("/api/v1/auth/me");
        setRole(me.role, me.id);
      } catch {
        // me 호출 실패해도 로그인 자체는 유지한다
      }
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "로그인에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDemo() {
    setError(null);
    setLoading(true);
    try {
      const data = await apiClient.post<TokenResponse>("/api/v1/auth/demo", {});
      login(data.access_token, "__demo__");
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "데모 로그인에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* 왼쪽: 브랜딩 패널 (모바일에서 숨김) */}
      <div className="hidden lg:flex flex-col justify-center px-12 bg-primary text-primary-foreground">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Bot className="h-8 w-8" />
            <span className="text-2xl font-bold">mystock.bot</span>
          </div>
          <p className="text-primary-foreground/70 text-sm">
            한국 주식 자동매매 플랫폼
          </p>
        </div>

        <ul className="space-y-6">
          {FEATURES.map(({ icon: Icon, label, desc }) => (
            <li key={label} className="flex items-start gap-4">
              <div className="mt-0.5 p-2 rounded-md bg-primary-foreground/10">
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <p className="font-medium">{label}</p>
                <p className="text-sm text-primary-foreground/70">{desc}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* 오른쪽: 로그인 폼 */}
      <div className="flex items-center justify-center p-8">
        <Card className="w-full max-w-sm">
          <CardHeader>
            {/* 모바일에서만 로고 표시 */}
            <div className="flex items-center gap-2 mb-1 lg:hidden">
              <Bot className="h-5 w-5 text-primary" />
              <span className="font-semibold text-primary">mystock.bot</span>
            </div>
            <CardTitle className="text-xl">로그인</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="email">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="이메일 입력"
                  autoComplete="email"
                  disabled={loading}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">비밀번호</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="비밀번호 입력"
                  autoComplete="current-password"
                  disabled={loading}
                />
              </div>
              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "로그인 중..." : "로그인"}
              </Button>
            </form>

            <div className="flex items-center gap-3">
              <Separator className="flex-1" />
              <span className="text-xs text-muted-foreground">또는</span>
              <Separator className="flex-1" />
            </div>

            <Button
              variant="outline"
              className="w-full"
              onClick={handleDemo}
              disabled={loading}
            >
              데모 보기
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
