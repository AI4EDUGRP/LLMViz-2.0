import React from "react";
import { motion } from "framer-motion";
import { CheckCircle2, ScanLine, Upload, Zap } from "lucide-react";
import { PageShell } from "./ui/page-shell";
import { EvaluatorShowcase, SynthMark } from "./ui/synth-visuals";

interface MagicEvaluatorProps {
  title?: string;
  subtitle?: string;
}

const steps = [
  { icon: Upload, text: "Upload PNG or JPG", desc: "Drop your chart image" },
  { icon: Zap, text: "AI quality analysis", desc: "Labels, colors, clarity" },
  { icon: CheckCircle2, text: "Actionable feedback", desc: "Improve your viz" },
];

const MagicEvaluator: React.FC<MagicEvaluatorProps> = ({
  title = "Visualization Evaluator",
  subtitle = "Upload your chart image below. Our AI will review labels, colors, and overall effectiveness.",
}) => {
  return (
    <PageShell>
      <div className="relative mb-4 overflow-hidden rounded-[24px] border border-black/5 bg-white/75 p-5 shadow-[0_14px_42px_rgba(80,70,160,0.09)] backdrop-blur sm:p-6">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(520px 280px at 84% 18%, rgba(91,140,90,0.22), transparent 70%), radial-gradient(440px 260px at 12% 88%, rgba(208,107,156,0.14), transparent 70%)",
          }}
        />
        <motion.div
          className="pointer-events-none absolute right-8 top-6 hidden opacity-15 lg:block"
          animate={{ rotate: [0, -10, 0], y: [0, -8, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        >
          <SynthMark className="h-24 w-24 text-emerald-400" />
        </motion.div>

        <div className="relative grid grid-cols-1 items-center gap-5 lg:grid-cols-[1fr_340px]">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 inline-flex items-center gap-2 rounded-full border border-black/5 bg-white/80 px-3 py-1.5 text-[10px] uppercase tracking-[0.18em] text-neutral-500 shadow-sm"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              <ScanLine className="h-3.5 w-3.5 text-neutral-800" />
              Visualization Quality Engine
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
              {steps.map((step, i) => (
                <motion.div
                  key={step.text}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.16 + i * 0.06 }}
                  className="flex items-center gap-2 rounded-2xl border border-black/5 bg-white/70 px-3 py-2.5 shadow-sm"
                >
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-neutral-950 text-[11px] font-bold text-white">
                    {i + 1}
                  </span>
                  <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                    <step.icon className="h-4 w-4" />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-neutral-800">{step.text}</p>
                    <p className="text-[11px] text-neutral-400">{step.desc}</p>
                  </div>
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
            <EvaluatorShowcase accent="#5b8c5a" />
          </motion.div>
        </div>
      </div>
    </PageShell>
  );
};

export default MagicEvaluator;
