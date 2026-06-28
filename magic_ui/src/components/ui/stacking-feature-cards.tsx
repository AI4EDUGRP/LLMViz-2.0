import React from "react";
import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { cn } from "../../lib/utils";

export interface FeatureRowData {
  tag: string;
  icon: React.ComponentType<{ className?: string }>;
  accent: string;
  panel: string;
  title: string;
  body: string;
  visual: "chat" | "analyze" | "network";
}

interface StackingFeatureCardsProps {
  rows: FeatureRowData[];
  monoFont: string;
  onLearnMore: () => void;
  renderVisual: (visual: FeatureRowData["visual"], accent: string) => React.ReactNode;
  renderEyebrow: (
    icon: FeatureRowData["icon"],
    children: React.ReactNode,
  ) => React.ReactNode;
}

/**
 * Feature cards with scroll-triggered entrance animations.
 * No inner scroll container — uses the main page scroll only (works in Streamlit).
 */
export default function StackingFeatureCards({
  rows,
  monoFont,
  onLearnMore,
  renderVisual,
  renderEyebrow,
}: StackingFeatureCardsProps) {
  return (
    <section className="relative pb-4">
      {rows.map((row, index) => (
        <motion.div
          key={row.title}
          initial={{ opacity: 0, y: 48, scale: 0.97 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.55, ease: "easeOut", delay: index * 0.05 }}
          className={cn("relative", index > 0 && "-mt-10 sm:-mt-14")}
          style={{ zIndex: index + 1 }}
        >
          <div
            className={cn(
              "grid grid-cols-1 gap-8 overflow-hidden rounded-[28px] p-8 sm:p-12 lg:grid-cols-2 lg:items-center shadow-[0_16px_48px_rgba(0,0,0,0.06)]",
            )}
            style={{ background: row.panel }}
          >
            <div className={index % 2 === 1 ? "lg:order-2" : ""}>
              {renderEyebrow(row.icon, row.tag)}
              <h3 className="mt-4 text-[28px] font-bold leading-tight tracking-tight sm:text-[36px]">
                {row.title}
              </h3>
              <p className="mt-4 max-w-md text-[15px] leading-relaxed text-neutral-600">{row.body}</p>
              <button
                type="button"
                onClick={onLearnMore}
                className="mt-6 inline-flex items-center gap-1.5 text-[13px] uppercase tracking-[0.12em] text-neutral-900"
                style={{ fontFamily: monoFont }}
              >
                Learn more <ArrowUpRight className="h-4 w-4" />
              </button>
            </div>
            <div
              className={cn(
                "relative h-[260px] rounded-2xl border border-black/5 bg-white/40 p-6 backdrop-blur-sm",
                index % 2 === 1 ? "lg:order-1" : "",
              )}
            >
              {renderVisual(row.visual, row.accent)}
            </div>
          </div>
        </motion.div>
      ))}
    </section>
  );
}
