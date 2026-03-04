"use client";

import { useAdminUsers, useApproveUser, useDeactivateUser } from "@/hooks/use-admin";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

/** 관리자 사용자 관리 탭 컴포넌트 */
export function UserTab() {
  const { data: users, isLoading } = useAdminUsers();
  const currentUserId = useAuthStore((state) => state.userId);
  const approveMutation = useApproveUser();
  const deactivateMutation = useDeactivateUser();

  return (
    <div className="space-y-4">
      {isLoading ? (
        <p className="text-sm text-muted-foreground">불러오는 중...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>사용자명</TableHead>
              <TableHead>이메일</TableHead>
              <TableHead>역할</TableHead>
              <TableHead>승인상태</TableHead>
              <TableHead>활성상태</TableHead>
              <TableHead>가입일</TableHead>
              <TableHead>액션</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users && users.length > 0 ? (
              users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="text-sm">{user.id}</TableCell>
                  <TableCell className="font-medium">{user.username}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {user.email ?? "-"}
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.role === "admin" ? "default" : "secondary"}>
                      {user.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.is_approved ? "default" : "destructive"}>
                      {user.is_approved ? "승인됨" : "미승인"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.is_active ? "default" : "secondary"}>
                      {user.is_active ? "활성" : "비활성"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(user.created_at).toLocaleDateString("ko-KR")}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {/* 미승인 사용자만 승인 버튼 표시 */}
                      {!user.is_approved && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => approveMutation.mutate({ id: user.id })}
                          disabled={approveMutation.isPending && approveMutation.variables?.id === user.id}
                        >
                          승인
                        </Button>
                      )}
                      {/* 활성 상태이고 자기 자신이 아닌 경우만 비활성화 버튼 표시 */}
                      {user.is_active && user.id !== currentUserId && (
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => deactivateMutation.mutate({ id: user.id })}
                          disabled={deactivateMutation.isPending && deactivateMutation.variables?.id === user.id}
                        >
                          비활성화
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                  사용자가 없습니다.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
