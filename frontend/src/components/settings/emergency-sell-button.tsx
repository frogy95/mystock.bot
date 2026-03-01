"use client";

import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface EmergencySellButtonProps {
  onConfirm: () => void;
}

export function EmergencySellButton({ onConfirm }: EmergencySellButtonProps) {
  return (
    <AlertDialog>
      {/* 긴급 매도 트리거 버튼 */}
      <AlertDialogTrigger asChild>
        <Button
          size="lg"
          variant="destructive"
          className="w-full bg-red-600 hover:bg-red-700 text-white font-bold"
        >
          긴급 전체 매도
        </Button>
      </AlertDialogTrigger>

      {/* 확인 다이얼로그 */}
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>정말로 전체 매도하시겠습니까?</AlertDialogTitle>
          <AlertDialogDescription>
            모든 보유 종목을 현재가에 즉시 매도합니다. 이 작업은 되돌릴 수
            없습니다.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>취소</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className="bg-red-600 hover:bg-red-700 text-white"
          >
            전체 매도 실행
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
