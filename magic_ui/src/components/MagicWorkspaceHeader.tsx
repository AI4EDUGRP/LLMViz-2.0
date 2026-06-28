import React from "react";
import { motion } from "framer-motion";
import { BarChart3, FileUp, MessageSquareText, Sparkles, Wand2 } from "lucide-react";
import { PageShell } from "./ui/page-shell";
import { GeneratorShowcase, SynthMark } from "./ui/synth-visuals";

interface MagicWorkspaceHeaderProps {
  title: string;
  subtitle: string;
  icon?: "generator" | "evaluator";
}

const MagicWorkspaceHeader: React.FC<MagicWorkspaceHeaderProps> = ({
  title,
  subtitle,
  icon = "generator",
}) => {
  const Icon = icon === "evaluator" ? Sparkles : BarChart3;
  return (
    <PageShell>
      <div className="relative overflow-hidden rounded-[24px] border border-black/5 bg-white/75 p-5 shadow-[0_14px_42px_rgba(80,70,160,0.09)] backdrop-blur sm:p-6">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(520px 280px at 86% 12%, rgba(167,139,250,0.24), transparent 70%), radial-gradient(440px 260px at 12% 88%, rgba(91,140,90,0.16), transparent 70%)",
          }}
        />
        <motion.div
          className="pointer-events-none absolute right-8 top-6 hidden opacity-15 lg:block"
          animate={{ rotate: [0, 10, 0], y: [0, -8, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        >
          <SynthMark className="h-24 w-24 text-violet-400" />
        </motion.div>

        <div className="relative grid grid-cols-1 items-center gap-5 lg:grid-cols-[1fr_340px]">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 inline-flex items-center gap-2 rounded-full border border-black/5 bg-white/80 px-3 py-1.5 text-[10px] uppercase tracking-[0.18em] text-neutral-500 shadow-sm"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              <Icon className="h-3.5 w-3.5 text-neutral-800" />
              AI Visualization Workspace
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="max-w-[720px] text-[30px] font-extrabold leading-[1.08] tracking-tight text-neutral-950 sm:text-[38px]"
            >
              {title}
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mt-3 max-w-[640px] text-[14px] leading-relaxed text-neutral-500 sm:text-[15px]"
            >
              {subtitle}
            </motion.p>

            <div className="mt-5 grid grid-cols-1 gap-2 sm:grid-cols-3">
              {[
                { icon: FileUp, label: "Upload data", color: "#5b8c5a" },
                { icon: MessageSquareText, label: "Ask in chat", color: "#6d5bd0" },
                { icon: Wand2, label: "Generate visual", color: "#d06b9c" },
              ].map((step, i) => (
                <motion.div
                  key={step.label}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.16 + i * 0.06 }}
                  className="flex items-center gap-2 rounded-2xl border border-black/5 bg-white/70 px-3 py-2.5 shadow-sm"
                >
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-neutral-950 text-[11px] font-bold text-white">
                    {i + 1}
                  </span>
                  <span
                    className="flex h-7 w-7 items-center justify-center rounded-xl"
                    style={{ background: `${step.color}1f`, color: step.color }}
                  >
                    <step.icon className="h-4 w-4" />
                  </span>
                  <span className="text-sm font-semibold text-neutral-800">{step.label}</span>
                </motion.div>
              ))}
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96, x: 20 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ delay: 0.12 }}
            className="hidden h-[190px] rounded-[22px] border border-black/5 bg-white/60 p-4 shadow-[0_14px_42px_rgba(80,70,160,0.10)] backdrop-blur lg:block"
          >
            <GeneratorShowcase accent="#6d5bd0" />
          </motion.div>
        </div>
      </div>
    </PageShell>
  );
};

export default MagicWorkspaceHeader;
