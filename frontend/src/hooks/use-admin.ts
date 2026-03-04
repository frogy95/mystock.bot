"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import type { AdminInvitation, AdminUser, CreateInvitationRequest } from "@/lib/api/types";

/** 초대코드 목록 조회 훅 */
export function useInvitations() {
  return useQuery<AdminInvitation[]>({
    queryKey: ["admin", "invitations"],
    queryFn: () => apiClient.get<AdminInvitation[]>("/api/v1/admin/invitations"),
    staleTime: 30_000,
  });
}

/** 초대코드 생성 훅 */
export function useCreateInvitation() {
  const queryClient = useQueryClient();
  return useMutation<AdminInvitation, Error, CreateInvitationRequest>({
    mutationFn: (body) =>
      apiClient.post<AdminInvitation>("/api/v1/admin/invitations", body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "invitations"] });
      toast.success("초대코드가 생성되었습니다.");
    },
    onError: (err) => {
      toast.error(err instanceof Error ? err.message : "초대코드 생성에 실패했습니다.");
    },
  });
}

/** 사용자 목록 조회 훅 */
export function useAdminUsers() {
  return useQuery<AdminUser[]>({
    queryKey: ["admin", "users"],
    queryFn: () => apiClient.get<AdminUser[]>("/api/v1/admin/users"),
    staleTime: 30_000,
  });
}

/** 사용자 승인 훅 */
export function useApproveUser() {
  const queryClient = useQueryClient();
  return useMutation<AdminUser, Error, { id: number }>({
    mutationFn: ({ id }) =>
      apiClient.put<AdminUser>(`/api/v1/admin/users/${id}/approve`, {}),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      toast.success(`${data.username} 사용자를 승인했습니다.`);
    },
    onError: (err) => {
      toast.error(err instanceof Error ? err.message : "사용자 승인에 실패했습니다.");
    },
  });
}

/** 사용자 비활성화 훅 */
export function useDeactivateUser() {
  const queryClient = useQueryClient();
  return useMutation<AdminUser, Error, { id: number }>({
    mutationFn: ({ id }) =>
      apiClient.put<AdminUser>(`/api/v1/admin/users/${id}/deactivate`, {}),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      toast.success(`${data.username} 사용자를 비활성화했습니다.`);
    },
    onError: (err) => {
      toast.error(err instanceof Error ? err.message : "사용자 비활성화에 실패했습니다.");
    },
  });
}
