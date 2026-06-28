import React from "react";
import { cn } from "../../lib/utils";

interface RevenueCardProps extends React.HTMLAttributes<HTMLDivElement> {
  dark?: boolean;
}

export function RevenueCard({ children, className, dark = false, ...props }: RevenueCardProps) {
  return (
    <div
      className={cn(
        "rounded-[8px] border p-6",
        dark
          ? "border-[#202020] bg-[#202020] text-white"
          : "border-[#202020] bg-white text-[#202020]",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
