"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Copy, Link } from "lucide-react";
import { useInvitations, useCreateInvitation } from "@/hooks/use-admin";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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

/** 초대코드 상태를 계산하여 반환한다 */
function getInvitationStatus(isUsed: boolean, expiresAt: string): "유효" | "사용됨" | "만료됨" {
  if (isUsed) return "사용됨";
  if (new Date(expiresAt) < new Date()) return "만료됨";
  return "유효";
}

/** 상태별 Badge variant 반환 */
function getStatusVariant(status: "유효" | "사용됨" | "만료됨") {
  if (status === "유효") return "default";
  if (status === "사용됨") return "secondary";
  return "destructive";
}

/** 관리자 초대코드 탭 컴포넌트 */
export function InvitationTab() {
  const [expiresDays, setExpiresDays] = useState("7");
  const { data: invitations, isLoading } = useInvitations();
  const createMutation = useCreateInvitation();

  // 코드 텍스트 클립보드 복사
  const handleCopyCode = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      toast.success("코드가 복사되었습니다.");
    } catch {
      toast.error("클립보드 복사에 실패했습니다.");
    }
  };

  // 회원가입 링크 클립보드 복사
  const handleCopyLink = async (code: string) => {
    const link = `${window.location.origin}/register?code=${code}`;
    try {
      await navigator.clipboard.writeText(link);
      toast.success("초대 링크가 복사되었습니다.");
    } catch {
      toast.error("클립보드 복사에 실패했습니다.");
    }
  };

  // 초대코드 생성 핸들러
  const handleCreate = () => {
    createMutation.mutate({ expires_days: Number(expiresDays) });
  };

  return (
    <div className="space-y-4">
      {/* 생성 폼 */}
      <div className="flex items-center gap-3">
        <Select value={expiresDays} onValueChange={setExpiresDays}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="유효기간 선택" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1">1일</SelectItem>
            <SelectItem value="3">3일</SelectItem>
            <SelectItem value="7">7일</SelectItem>
            <SelectItem value="30">30일</SelectItem>
          </SelectContent>
        </Select>
        <Button onClick={handleCreate} disabled={createMutation.isPending}>
          {createMutation.isPending ? "생성 중..." : "초대코드 생성"}
        </Button>
      </div>

      {/* 초대코드 목록 테이블 */}
      {isLoading ? (
        <p className="text-sm text-muted-foreground">불러오는 중...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>코드</TableHead>
              <TableHead>상태</TableHead>
              <TableHead>만료일</TableHead>
              <TableHead>액션</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {invitations && invitations.length > 0 ? (
              invitations.map((inv) => {
                const status = getInvitationStatus(inv.is_used, inv.expires_at);
                return (
                  <TableRow key={inv.id}>
                    <TableCell className="font-mono text-sm">{inv.code}</TableCell>
                    <TableCell>
                      <Badge variant={getStatusVariant(status)}>{status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(inv.expires_at).toLocaleDateString("ko-KR")}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopyCode(inv.code)}
                          title="코드 복사"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopyLink(inv.code)}
                          title="초대 링크 복사"
                        >
                          <Link className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-muted-foreground py-8">
                  초대코드가 없습니다.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
