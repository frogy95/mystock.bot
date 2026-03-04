"use client";

import { Shield } from "lucide-react";
import { AdminGuard } from "@/components/layout/admin-guard";
import { InvitationTab } from "@/components/admin/invitation-tab";
import { UserTab } from "@/components/admin/user-tab";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

/** 관리자 대시보드 페이지 - 초대코드 관리 및 사용자 관리 탭 제공 */
export default function AdminPage() {
  return (
    <AdminGuard>
      <div className="p-6 space-y-6">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          <h1 className="text-2xl font-bold">관리자 대시보드</h1>
        </div>
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
