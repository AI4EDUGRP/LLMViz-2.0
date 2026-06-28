import React from "react";

export function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative w-full overflow-hidden rounded-[28px] bg-[#fbfbfa]">
      <div
        className="pointer-events-none absolute inset-0 opacity-80"
        style={{
          backgroundImage:
            "radial-gradient(circle at 16% 18%, rgba(199,240,224,0.46) 0%, transparent 38%), radial-gradient(circle at 84% 6%, rgba(231,221,247,0.64) 0%, transparent 42%), radial-gradient(circle at 52% 100%, rgba(223,232,251,0.58) 0%, transparent 45%)",
        }}
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.24]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(17,24,39,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(17,24,39,0.04) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />
      <div className="relative z-10 px-1 py-2">{children}</div>
    </div>
  );
}
