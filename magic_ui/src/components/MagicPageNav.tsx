import React, { useCallback } from "react";
import { Streamlit } from "streamlit-component-lib";
import { LogOut } from "lucide-react";
import { VisualStatsLogo } from "./ui/synth-visuals";

interface MagicPageNavProps {
  active?: string;
  isAdmin?: boolean;
}

const MONO = "var(--font-mono)";
const SYNTH = "var(--font-synth)";

const MagicPageNav: React.FC<MagicPageNavProps> = ({ active = "home", isAdmin = false }) => {
  const emit = useCallback((action: string, target?: string) => {
    Streamlit.setComponentValue({ action, target, timestamp: Date.now() });
  }, []);

  const links = [
    { label: "Home", target: "home" },
    { label: "Generator", target: "viz_generator" },
    { label: "Evaluator", target: "viz_evaluator" },
    ...(isAdmin ? [{ label: "Analytics", target: "analytics_dashboard" }] : []),
  ];

  return (
    <div className="w-full bg-[#fbfbfa] px-6 pb-4 pt-8 sm:px-10 lg:px-16 xl:px-20" style={{ fontFamily: SYNTH }}>
      <nav className="flex min-h-[64px] items-center justify-between gap-4">
        <button
          type="button"
          onClick={() => emit("navigate", "home")}
          className="flex items-center gap-3 text-neutral-900"
        >
          <VisualStatsLogo className="h-10 w-10" />
          <span className="text-[20px] font-bold tracking-tight">VisualStats</span>
        </button>

        <div className="flex items-center gap-1.5 rounded-2xl border border-black/5 bg-white/85 px-3 py-2 shadow-[0_10px_34px_rgba(0,0,0,0.07)] backdrop-blur">
          {links.map((link) => {
            const selected = active === link.target;
            return (
              <button
                key={link.target}
                type="button"
                onClick={() => emit("navigate", link.target)}
                className={`rounded-xl px-4 py-2 text-[13px] uppercase tracking-[0.1em] transition-colors ${
                  selected
                    ? "bg-neutral-900 text-white"
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                }`}
                style={{ fontFamily: MONO }}
              >
                {link.label}
              </button>
            );
          })}
          <button
            type="button"
            onClick={() => emit("logout")}
            className="ml-1 inline-flex items-center gap-1.5 rounded-xl px-4 py-2.5 text-[13px] uppercase tracking-[0.1em] text-neutral-500 transition-colors hover:bg-red-50 hover:text-red-600"
            style={{ fontFamily: MONO }}
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </nav>
    </div>
  );
};

export default MagicPageNav;
