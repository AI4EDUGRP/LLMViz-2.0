import React from "react";
import { motion } from "framer-motion";
import { BarChart3, FileUp, MessageSquareText, MousePointer2, Wand2 } from "lucide-react";
import { MagicCard } from "./ui/magic-card";
import { SynthMark } from "./ui/synth-visuals";

interface MagicEmptyCanvasProps {
  title?: string;
  description?: string;
}

const MagicEmptyCanvas: React.FC<MagicEmptyCanvasProps> = ({
  title = "Visualization Canvas",
  description = "Upload a dataset on the left to start generating charts.",
}) => {
  return (
    <MagicCard
      noPadding
      gradientColor="rgba(109,91,208,0.16)"
      className="border-dashed border-black/10 bg-white/80"
    >
      <div className="relative flex min-h-[460px] flex-col items-center justify-center overflow-hidden p-8 text-center">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(420px 220px at 50% 26%, rgba(109,91,208,0.14), transparent 70%), radial-gradient(360px 220px at 18% 80%, rgba(91,140,90,0.12), transparent 70%)",
          }}
        />
        <motion.div
          className="pointer-events-none absolute opacity-10"
          animate={{ rotate: [0, 12, 0], scale: [1, 1.04, 1] }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        >
          <SynthMark className="h-52 w-52 text-violet-500" />
        </motion.div>

        <div className="relative mb-8">
          <motion.div
            className="absolute inset-0 rounded-full bg-violet-200/50 blur-2xl"
            animate={{ scale: [1, 1.18, 1], opacity: [0.4, 0.75, 0.4] }}
            transition={{ duration: 3.2, repeat: Infinity }}
          />
          <motion.div
            className="relative rounded-[24px] bg-neutral-950 p-5 text-white shadow-[0_18px_50px_rgba(0,0,0,0.18)]"
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          >
            <BarChart3 className="h-11 w-11" />
          </motion.div>
          <motion.div
            className="absolute -right-8 -top-4 rounded-xl border border-black/5 bg-white px-3 py-2 text-[11px] font-semibold text-neutral-700 shadow-lg"
            animate={{ x: [0, 6, 0], y: [0, -5, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          >
            <MousePointer2 className="mr-1 inline h-3.5 w-3.5 text-violet-600" />
            ready
          </motion.div>
        </div>

        <div className="relative">
          <h3 className="text-[26px] font-extrabold tracking-tight text-neutral-950">{title}</h3>
          <p className="mx-auto mt-3 max-w-md text-[15px] leading-relaxed text-neutral-500">{description}</p>
          <div className="mt-8 grid grid-cols-1 gap-3 sm:grid-cols-3">
            {[
              { icon: FileUp, label: "Upload data", color: "#5b8c5a" },
              { icon: MessageSquareText, label: "Ask naturally", color: "#6d5bd0" },
              { icon: Wand2, label: "Get a chart", color: "#d06b9c" },
            ].map((step, i) => (
              <motion.span
                key={step.label}
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-black/5 bg-white/80 px-4 py-3 text-sm font-semibold text-neutral-700 shadow-sm"
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <step.icon className="h-4 w-4" style={{ color: step.color }} />
                {step.label}
              </motion.span>
            ))}
          </div>
        </div>
      </div>
    </MagicCard>
  );
};

export default MagicEmptyCanvas;
