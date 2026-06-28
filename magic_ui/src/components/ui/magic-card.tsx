import { motion, useMotionTemplate, useMotionValue } from "framer-motion";
import React, { useCallback, useRef } from "react";
import { cn } from "../../lib/utils";

export interface MagicCardProps extends React.HTMLAttributes<HTMLDivElement> {
  gradientSize?: number;
  gradientColor?: string;
  gradientOpacity?: number;
  noPadding?: boolean;
}

export function MagicCard({
  children,
  className,
  gradientSize = 200,
  gradientColor = "rgba(59, 130, 246, 0.15)",
  gradientOpacity = 0.7,
  noPadding = false,
  ...props
}: MagicCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(-gradientSize);
  const mouseY = useMotionValue(-gradientSize);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!cardRef.current) return;
      const { left, top } = cardRef.current.getBoundingClientRect();
      mouseX.set(e.clientX - left);
      mouseY.set(e.clientY - top);
    },
    [mouseX, mouseY],
  );

  const handleMouseOut = useCallback(() => {
    mouseX.set(-gradientSize);
    mouseY.set(-gradientSize);
  }, [mouseX, mouseY, gradientSize]);

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseOut}
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-[0_8px_30px_rgba(30,64,175,0.08)] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_12px_40px_rgba(30,64,175,0.12)]",
        className,
      )}
      {...props}
    >
      <div className={cn("relative z-10 w-full", !noPadding && "p-5")}>{children}</div>
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          background: useMotionTemplate`
            radial-gradient(${gradientSize}px circle at ${mouseX}px ${mouseY}px, ${gradientColor}, transparent 80%)
          `,
          opacity: gradientOpacity,
        }}
      />
    </div>
  );
}
