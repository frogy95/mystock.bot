import { redirect } from "next/navigation";

// 루트 경로 접근 시 대시보드로 리다이렉트
export default function Home() {
  redirect("/dashboard");
}
