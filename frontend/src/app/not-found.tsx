import Link from "next/link";
import { Button } from "@/components/ui/button";

// 404 Not Found 페이지
export default function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <h2 className="text-4xl font-bold text-muted-foreground">404</h2>
      <p className="text-lg font-medium">페이지를 찾을 수 없습니다</p>
      <p className="max-w-md text-sm text-muted-foreground">
        요청하신 페이지가 존재하지 않거나 이동되었습니다.
      </p>
      <Button asChild variant="outline">
        <Link href="/dashboard">홈으로 돌아가기</Link>
      </Button>
    </div>
  );
}
