/**
 * Next.js 미들웨어 — 서버사이드 인증 가드
 * auth-token 쿠키가 없으면 /login으로 리다이렉트한다.
 * /login, /api, /_next 경로는 제외한다.
 */
import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("auth-token")?.value;

  // /login, /register는 인증 없이 접근 가능한 공개 경로
  const publicPaths = ["/login", "/register"];
  if (!token && !publicPaths.includes(pathname)) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|api/).*)",
  ],
};
