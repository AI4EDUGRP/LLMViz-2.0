import React from "react";
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from "framer-motion";
import {
  Sparkles,
  MousePointer2,
  Mail,
  Clock,
  TrendingUp,
  Activity,
  Wand2,
  Check,
  ScanLine,
} from "lucide-react";

/**
 * A small pointer cursor that floats between a series of points.
 * Used to add life to otherwise static illustrations.
 */
function FloatingCursor({
  points,
  color = "#1a1a1a",
  duration = 6,
}: {
  points: { x: number; y: number }[];
  color?: string;
  duration?: number;
}) {
  return (
    <motion.div
      className="pointer-events-none absolute z-20"
      initial={{ x: points[0].x, y: points[0].y, opacity: 0 }}
      animate={{
        x: points.map((p) => p.x),
        y: points.map((p) => p.y),
        opacity: [0, 1, 1, 1, 1, 1],
      }}
      transition={{
        duration,
        times: points.map((_, i) => i / (points.length - 1)),
        repeat: Infinity,
        repeatType: "reverse",
        ease: "easeInOut",
      }}
    >
      <MousePointer2
        className="h-5 w-5 drop-shadow-sm"
        style={{ color, fill: color }}
      />
    </motion.div>
  );
}

/** Animated line chart that draws itself and has a value dot tracking a floating cursor. */
export function FloatingLineChart({ accent = "#6d5bd0" }: { accent?: string }) {
  const w = 380;
  const h = 220;
  const pts = [
    [10, 170],
    [70, 120],
    [130, 145],
    [190, 80],
    [250, 110],
    [310, 45],
    [370, 70],
  ];
  const path = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p[0]},${p[1]}`).join(" ");
  const area = `${path} L${pts[pts.length - 1][0]},${h} L${pts[0][0]},${h} Z`;

  return (
    <div className="relative h-full w-full">
      <svg viewBox={`0 0 ${w} ${h}`} className="h-full w-full">
        <defs>
          <linearGradient id="lineFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={accent} stopOpacity="0.28" />
            <stop offset="100%" stopColor={accent} stopOpacity="0" />
          </linearGradient>
        </defs>
        {[40, 90, 140, 190].map((y) => (
          <line key={y} x1="0" y1={y} x2={w} y2={y} stroke="#00000010" strokeWidth="1" />
        ))}
        <motion.path
          d={area}
          fill="url(#lineFill)"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.6 }}
        />
        <motion.path
          d={path}
          fill="none"
          stroke={accent}
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.6, ease: "easeInOut" }}
        />
        {pts.map((p, i) => (
          <motion.circle
            key={i}
            cx={p[0]}
            cy={p[1]}
            r="4"
            fill="#fff"
            stroke={accent}
            strokeWidth="2.5"
            initial={{ scale: 0 }}
            whileInView={{ scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 + i * 0.12, type: "spring", stiffness: 300 }}
          />
        ))}
      </svg>
      <div className="absolute inset-0">
        <FloatingCursor
          color={accent}
          duration={7}
          points={pts.map((p) => ({ x: p[0] * 0.92, y: p[1] * 0.92 }))}
        />
      </div>
    </div>
  );
}

/** Animated bar chart with a floating cursor hovering over the tallest bars. */
export function FloatingBarChart({ accent = "#5b8c5a" }: { accent?: string }) {
  const bars = [55, 78, 42, 92, 66, 84, 50];
  return (
    <div className="relative h-full w-full px-2">
      <div className="flex h-full items-end justify-between gap-2 pb-2">
        {bars.map((v, i) => (
          <motion.div
            key={i}
            className="relative flex-1 rounded-t-md"
            style={{
              background: `linear-gradient(180deg, ${accent} 0%, ${accent}88 100%)`,
            }}
            initial={{ height: 0 }}
            whileInView={{ height: `${v}%` }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, delay: i * 0.08, ease: "easeOut" }}
          />
        ))}
      </div>
      <FloatingCursor
        color={accent}
        duration={6}
        points={[
          { x: 40, y: 40 },
          { x: 150, y: 25 },
          { x: 230, y: 60 },
          { x: 300, y: 15 },
          { x: 120, y: 50 },
        ]}
      />
    </div>
  );
}

/** "Ask me anything" chat mockup, mirroring the SynthAI automation card. */
export function ChatMockup({ accent = "#5b8c5a" }: { accent?: string }) {
  const suggestions = [
    { icon: Mail, label: "Plot revenue by month" },
    { icon: Clock, label: "Generate trend analysis" },
  ];
  return (
    <div className="relative flex h-full w-full flex-col justify-center gap-4">
      {/* stacked faux cards behind input */}
      <div className="relative">
        <div className="absolute -top-3 left-2 right-2 h-10 rounded-2xl border border-black/5 bg-white/50" />
        <div className="absolute -top-1.5 left-1 right-1 h-10 rounded-2xl border border-black/5 bg-white/70" />
        <motion.div
          className="relative flex items-center gap-3 rounded-2xl px-5 py-4 text-white shadow-lg"
          style={{ background: accent }}
          animate={{ boxShadow: [`0 8px 24px ${accent}33`, `0 8px 34px ${accent}55`, `0 8px 24px ${accent}33`] }}
          transition={{ duration: 2.4, repeat: Infinity }}
        >
          <Sparkles className="h-4 w-4 opacity-90" />
          <span className="text-[14px] opacity-90">| Ask me anything....</span>
          <motion.span
            className="ml-auto"
            animate={{ x: [0, -4, 0], y: [0, -3, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <MousePointer2 className="h-4 w-4" />
          </motion.span>
        </motion.div>
      </div>
      <div className="space-y-3 pl-1">
        {suggestions.map((s, i) => (
          <motion.div
            key={s.label}
            className="flex items-center gap-2.5 text-[14px] text-neutral-700"
            initial={{ opacity: 0, x: -10 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 + i * 0.2 }}
          >
            <s.icon className="h-4 w-4" style={{ color: accent }} />
            {s.label}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

/** Document + magnifier illustration with floating cursor (analytics). */
export function AnalyzeVisual({ accent = "#6d5bd0" }: { accent?: string }) {
  return (
    <div className="relative flex h-full w-full items-center justify-center">
      <div className="relative">
        <div className="w-44 rounded-2xl border border-black/5 bg-white/70 p-5 shadow-sm">
          {[80, 60, 90, 50, 70].map((wd, i) => (
            <motion.div
              key={i}
              className="mb-2.5 h-2 rounded-full"
              style={{ width: `${wd}%`, background: i === 0 ? accent : "#0000001a" }}
              initial={{ scaleX: 0, originX: 0 }}
              whileInView={{ scaleX: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, duration: 0.6 }}
            />
          ))}
        </div>
        <motion.div
          className="absolute -bottom-6 -right-6 flex h-20 w-20 items-center justify-center rounded-full shadow-lg"
          style={{ background: `${accent}` }}
          animate={{ y: [0, -8, 0], rotate: [0, 6, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut" }}
        >
          <Sparkles className="h-8 w-8 text-white" />
        </motion.div>
      </div>
      <FloatingCursor
        color={accent}
        duration={5.5}
        points={[
          { x: 30, y: 30 },
          { x: 180, y: 70 },
          { x: 90, y: 140 },
          { x: 200, y: 120 },
        ] as { x: number; y: number }[]}
      />
    </div>
  );
}

/** Network of avatars connecting to a central node (AI Assistant). */
export function AssistNetwork({ accent = "#d06b9c" }: { accent?: string }) {
  const left = [18, 50, 82];
  const right = [25, 60];
  return (
    <div className="relative flex h-full w-full items-center justify-center">
      <svg viewBox="0 0 320 220" className="absolute inset-0 h-full w-full">
        {left.map((p, i) => (
          <motion.line
            key={`l${i}`}
            x1="40"
            y1={`${p * 2}`}
            x2="160"
            y2="110"
            stroke={accent}
            strokeWidth="1.5"
            strokeOpacity="0.5"
            strokeDasharray="4 4"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1, delay: i * 0.2 }}
          />
        ))}
        {right.map((p, i) => (
          <motion.line
            key={`r${i}`}
            x1="160"
            y1="110"
            x2="280"
            y2={`${p * 2.5}`}
            stroke={accent}
            strokeWidth="1.5"
            strokeOpacity="0.5"
            strokeDasharray="4 4"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1, delay: 0.3 + i * 0.2 }}
          />
        ))}
      </svg>
      <motion.div
        className="absolute left-1/2 top-1/2 flex h-16 w-16 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-2xl"
        style={{ background: `${accent}22` }}
        animate={{ scale: [1, 1.08, 1] }}
        transition={{ duration: 2.6, repeat: Infinity }}
      >
        <SynthMark className="h-8 w-8" style={{ color: accent }} />
      </motion.div>
      {[
        { x: "6%", y: "20%" },
        { x: "6%", y: "48%" },
        { x: "6%", y: "76%" },
        { x: "82%", y: "26%" },
        { x: "82%", y: "62%" },
      ].map((pos, i) => (
        <motion.div
          key={i}
          className="absolute h-8 w-8 rounded-full border-2 border-white shadow-md"
          style={{
            left: pos.x,
            top: pos.y,
            background: `linear-gradient(135deg, ${accent}, ${accent}99)`,
          }}
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 2 + i * 0.3, repeat: Infinity, ease: "easeInOut" }}
        />
      ))}
    </div>
  );
}

/** The SynthAI asterisk / flower mark. */
export function SynthMark({
  className,
  style,
}: {
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <svg viewBox="0 0 24 24" className={className} style={style} fill="currentColor">
      <path d="M12 2c.5 0 .9.4.9.9v5.2l3.7-3.7a.9.9 0 1 1 1.3 1.3l-3.7 3.7h5.2a.9.9 0 0 1 0 1.8h-5.2l3.7 3.7a.9.9 0 1 1-1.3 1.3l-3.7-3.7v5.2a.9.9 0 0 1-1.8 0v-5.2l-3.7 3.7a.9.9 0 1 1-1.3-1.3l3.7-3.7H3.6a.9.9 0 0 1 0-1.8h5.2L5.1 6.7a.9.9 0 1 1 1.3-1.3l3.7 3.7V2.9c0-.5.4-.9.9-.9z" />
    </svg>
  );
}

/** VisualStats brand mark: animated bars with the evaluation check ring. */
export function VisualStatsLogo({
  className,
  style,
}: {
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <motion.svg
      viewBox="0 0 64 64"
      className={className}
      style={style}
      fill="none"
      initial="hidden"
      animate="show"
      whileHover={{ scale: 1.05, rotate: -2 }}
    >
      <defs>
        <linearGradient id="vsBars" x1="8" y1="44" x2="34" y2="18" gradientUnits="userSpaceOnUse">
          <stop stopColor="#3f3cc9" />
          <stop offset="1" stopColor="#27b99d" />
        </linearGradient>
        <linearGradient id="vsCheck" x1="28" y1="16" x2="58" y2="48" gradientUnits="userSpaceOnUse">
          <stop stopColor="#1f8f98" />
          <stop offset="1" stopColor="#28c493" />
        </linearGradient>
      </defs>

      {[18, 31, 44].map((x, i) => (
        <motion.rect
          key={x}
          x={x - 13}
          y={[34, 23, 39][i]}
          width="8.5"
          height={[20, 31, 15][i]}
          rx="3"
          fill="url(#vsBars)"
          initial={{ scaleY: 0, originY: 1 }}
          animate={{ scaleY: 1 }}
          transition={{ duration: 0.55, delay: i * 0.08, ease: "easeOut" }}
        />
      ))}

      <motion.circle
        cx="43"
        cy="27"
        r="15"
        stroke="url(#vsCheck)"
        strokeWidth="5"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.18, ease: "easeInOut" }}
      />
      <motion.path
        d="M35.5 27.2 40.7 32.4 51.2 21.8"
        stroke="url(#vsCheck)"
        strokeWidth="5"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.65, delay: 0.65, ease: "easeOut" }}
      />
    </motion.svg>
  );
}

/* ------------------------------------------------------------------ */
/*  Viz Generator showcase: prompt types out, then a chart builds itself */
/* ------------------------------------------------------------------ */
export function GeneratorShowcase({ accent = "#6d5bd0" }: { accent?: string }) {
  const scenes = React.useMemo(
    () => [
      { prompt: "Plot monthly revenue as a line chart", kind: "line" as const },
      { prompt: "Show sales by region as bars", kind: "bars" as const },
      { prompt: "Break down traffic sources", kind: "donut" as const },
    ],
    [],
  );

  const [scene, setScene] = React.useState(0);
  const [typed, setTyped] = React.useState("");
  const [phase, setPhase] = React.useState<"typing" | "generating" | "done">("typing");

  // Typewriter + lifecycle loop.
  React.useEffect(() => {
    const full = scenes[scene].prompt;
    let i = 0;
    setTyped("");
    setPhase("typing");
    const typer = window.setInterval(() => {
      i += 1;
      setTyped(full.slice(0, i));
      if (i >= full.length) {
        window.clearInterval(typer);
        window.setTimeout(() => setPhase("generating"), 350);
        window.setTimeout(() => setPhase("done"), 1050);
        window.setTimeout(() => setScene((s) => (s + 1) % scenes.length), 3600);
      }
    }, 45);
    return () => window.clearInterval(typer);
  }, [scene, scenes]);

  const kind = scenes[scene].kind;

  return (
    <div className="flex h-full w-full flex-col">
      {/* Prompt bar */}
      <div className="flex items-center gap-2.5 rounded-2xl border border-black/5 bg-neutral-50 px-4 py-3">
        <Sparkles className="h-4 w-4 shrink-0" style={{ color: accent }} />
        <span className="min-h-[18px] text-[14px] text-neutral-700">
          {typed}
          {phase === "typing" && (
            <motion.span
              className="ml-0.5 inline-block h-[15px] w-[2px] translate-y-[2px]"
              style={{ background: accent }}
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 0.8, repeat: Infinity }}
            />
          )}
        </span>
        <motion.span
          className="ml-auto flex shrink-0 items-center gap-1 rounded-lg px-2.5 py-1.5 text-[11px] font-semibold text-white"
          style={{ background: accent }}
          animate={phase === "generating" ? { scale: [1, 0.92, 1] } : {}}
          transition={{ duration: 0.4 }}
        >
          <Wand2 className="h-3 w-3" /> Generate
        </motion.span>
      </div>

      {/* Generated chart canvas */}
      <div className="relative mt-4 flex-1 rounded-2xl border border-black/5 bg-white/60 p-4">
        <AnimatePresence mode="wait">
          {phase === "generating" ? (
            <motion.div
              key="loading"
              className="flex h-full items-center justify-center gap-2 text-[13px] text-neutral-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.span
                className="h-4 w-4 rounded-full border-2 border-neutral-300 border-t-transparent"
                animate={{ rotate: 360 }}
                transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
                style={{ borderTopColor: "transparent", borderColor: `${accent}55`, borderTopWidth: 2 }}
              />
              Generating chart…
            </motion.div>
          ) : phase === "done" ? (
            <motion.div
              key={`chart-${scene}`}
              className="h-full w-full"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
            >
              {kind === "line" && <MiniLine accent={accent} />}
              {kind === "bars" && (
                <div className="h-full pt-2">
                  <MiniBars accent={accent} />
                </div>
              )}
              {kind === "donut" && (
                <div className="flex h-full items-center justify-center">
                  <MiniDonut accent={accent} />
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              className="flex h-full items-center justify-center text-[12px] text-neutral-300"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              Describe a chart above…
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Viz Evaluator showcase: a chart gets scanned and scored on quality  */
/* ------------------------------------------------------------------ */
export function EvaluatorShowcase({ accent = "#5b8c5a" }: { accent?: string }) {
  const checks = React.useMemo(
    () => [
      { label: "Axis labels", score: 95 },
      { label: "Color contrast", score: 88 },
      { label: "Clarity", score: 82 },
      { label: "Data-ink ratio", score: 76 },
    ],
    [],
  );

  const [run, setRun] = React.useState(0); // bump to replay
  const [scanning, setScanning] = React.useState(true);
  const score = useMotionValue(0);
  const scoreSpring = useSpring(score, { stiffness: 50, damping: 16 });
  const [scoreText, setScoreText] = React.useState(0);
  const ringDash = useTransform(scoreSpring, (v) => `${(v / 100) * 264} 264`);

  React.useEffect(() => {
    setScanning(true);
    score.set(0);
    const t1 = window.setTimeout(() => {
      setScanning(false);
      score.set(86);
    }, 1500);
    const t2 = window.setTimeout(() => setRun((r) => r + 1), 6000);
    return () => {
      window.clearTimeout(t1);
      window.clearTimeout(t2);
    };
  }, [run, score]);

  React.useEffect(() => {
    const unsub = scoreSpring.on("change", (v) => setScoreText(Math.round(v)));
    return () => unsub();
  }, [scoreSpring]);

  return (
    <div className="flex h-full w-full gap-4">
      {/* Scanned chart + score ring */}
      <div className="relative flex w-[44%] flex-col items-center justify-center rounded-2xl border border-black/5 bg-neutral-50 p-4">
        {/* faux uploaded chart */}
        <div className="relative w-full overflow-hidden rounded-lg bg-white p-2">
          <div className="flex h-14 items-end justify-between gap-1">
            {[50, 80, 35, 65, 90, 45].map((v, i) => (
              <div
                key={i}
                className="flex-1 rounded-t-sm"
                style={{ height: `${v}%`, background: `${accent}${i % 2 ? "99" : "cc"}` }}
              />
            ))}
          </div>
          {/* scan line */}
          {scanning && (
            <motion.div
              className="absolute inset-x-0 h-[3px]"
              style={{ background: `linear-gradient(90deg,transparent,${accent},transparent)` }}
              initial={{ top: "0%" }}
              animate={{ top: ["0%", "100%", "0%"] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
            />
          )}
        </div>

        {/* score ring */}
        <div className="relative mt-3 flex items-center justify-center">
          <svg viewBox="0 0 100 100" className="h-20 w-20 -rotate-90">
            <circle cx="50" cy="50" r="42" fill="none" stroke="#00000010" strokeWidth="8" />
            <motion.circle
              cx="50"
              cy="50"
              r="42"
              fill="none"
              stroke={accent}
              strokeWidth="8"
              strokeLinecap="round"
              style={{ strokeDasharray: ringDash }}
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className="text-[18px] font-extrabold leading-none text-neutral-900">
              {scanning ? "…" : scoreText}
            </span>
            <span className="text-[9px] text-neutral-400">/ 100</span>
          </div>
        </div>
      </div>

      {/* Feedback checklist */}
      <div className="flex flex-1 flex-col justify-center gap-2.5">
        <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-neutral-400">
          <ScanLine className="h-3.5 w-3.5" style={{ color: accent }} />
          {scanning ? "Analyzing…" : "Feedback"}
        </div>
        {checks.map((c, i) => (
          <motion.div
            key={`${run}-${c.label}`}
            initial={{ opacity: 0, x: 12 }}
            animate={scanning ? { opacity: 0.3, x: 0 } : { opacity: 1, x: 0 }}
            transition={{ delay: scanning ? 0 : i * 0.12, duration: 0.4 }}
          >
            <div className="mb-1 flex items-center justify-between text-[12px]">
              <span className="flex items-center gap-1.5 text-neutral-700">
                <motion.span
                  className="flex h-3.5 w-3.5 items-center justify-center rounded-full"
                  style={{ background: scanning ? "#e5e5e5" : accent }}
                  initial={false}
                  animate={{ scale: scanning ? 0.8 : [0.8, 1.2, 1] }}
                  transition={{ delay: scanning ? 0 : i * 0.12 }}
                >
                  {!scanning && <Check className="h-2.5 w-2.5 text-white" strokeWidth={3} />}
                </motion.span>
                {c.label}
              </span>
              <span className="text-neutral-400">{scanning ? "" : c.score}</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-neutral-100">
              <motion.div
                className="h-full rounded-full"
                style={{ background: accent }}
                initial={{ width: 0 }}
                animate={{ width: scanning ? "0%" : `${c.score}%` }}
                transition={{ delay: scanning ? 0 : 0.2 + i * 0.12, duration: 0.7 }}
              />
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Interactive hero scene: floating chart cards + spring-physics cursor */
/* ------------------------------------------------------------------ */

/** A small glass card that drifts on its own and parallax-shifts toward the pointer. */
function FloatCard({
  className = "",
  style,
  depth = 1,
  px,
  py,
  delay = 0,
  drift = 10,
  children,
}: {
  className?: string;
  style?: React.CSSProperties;
  depth?: number;
  px: ReturnType<typeof useSpring>;
  py: ReturnType<typeof useSpring>;
  delay?: number;
  drift?: number;
  children: React.ReactNode;
}) {
  // Parallax: deeper cards move more with the pointer.
  const tx = useTransform(px, (v) => v * depth * 26);
  const ty = useTransform(py, (v) => v * depth * 26);
  return (
    <motion.div
      className={`absolute rounded-2xl border border-white/60 bg-white/70 shadow-[0_18px_50px_rgba(80,70,160,0.18)] backdrop-blur-md ${className}`}
      style={{ ...style, x: tx, y: ty }}
    >
      <motion.div
        animate={{ y: [0, -drift, 0] }}
        transition={{ duration: 4 + delay, repeat: Infinity, ease: "easeInOut", delay }}
      >
        {children}
      </motion.div>
    </motion.div>
  );
}

/** Mini self-drawing line chart used inside a float card. */
function MiniLine({ accent }: { accent: string }) {
  const pts = [4, 26, 14, 40, 22, 30, 28, 48, 36, 38, 44, 58];
  const d = pts
    .reduce<string[]>((acc, _, i) => {
      if (i % 2 === 0) {
        const x = (pts[i] / 48) * 100;
        const y = 64 - (pts[i + 1] / 64) * 64;
        acc.push(`${i === 0 ? "M" : "L"}${x},${y}`);
      }
      return acc;
    }, [])
    .join(" ");
  return (
    <svg viewBox="0 0 100 64" className="h-16 w-full">
      <defs>
        <linearGradient id="mlFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={accent} stopOpacity="0.3" />
          <stop offset="100%" stopColor={accent} stopOpacity="0" />
        </linearGradient>
      </defs>
      <motion.path
        d={`${d} L100,64 L0,64 Z`}
        fill="url(#mlFill)"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 0.8 }}
      />
      <motion.path
        d={d}
        fill="none"
        stroke={accent}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1.8, ease: "easeInOut" }}
      />
    </svg>
  );
}

/** Mini animated bar chart. */
function MiniBars({ accent }: { accent: string }) {
  const bars = [40, 70, 52, 88, 64];
  return (
    <div className="flex h-16 items-end justify-between gap-1.5">
      {bars.map((v, i) => (
        <motion.div
          key={i}
          className="flex-1 rounded-t-[4px]"
          style={{ background: `linear-gradient(180deg, ${accent}, ${accent}88)` }}
          initial={{ height: 0 }}
          animate={{ height: `${v}%` }}
          transition={{ duration: 0.8, delay: 0.3 + i * 0.1, ease: "easeOut" }}
        />
      ))}
    </div>
  );
}

/** Mini animated donut chart. */
function MiniDonut({ accent }: { accent: string }) {
  const r = 26;
  const c = 2 * Math.PI * r;
  return (
    <svg viewBox="0 0 70 70" className="h-16 w-16">
      <circle cx="35" cy="35" r={r} fill="none" stroke="#00000010" strokeWidth="9" />
      <motion.circle
        cx="35"
        cy="35"
        r={r}
        fill="none"
        stroke={accent}
        strokeWidth="9"
        strokeLinecap="round"
        strokeDasharray={c}
        transform="rotate(-90 35 35)"
        initial={{ strokeDashoffset: c }}
        animate={{ strokeDashoffset: c * 0.32 }}
        transition={{ duration: 1.6, ease: "easeInOut", delay: 0.4 }}
      />
    </svg>
  );
}

/**
 * The hero visualization: a glowing aurora backdrop, several floating
 * chart cards with pointer parallax, drifting particles, and a cursor
 * that tours the cards using spring physics (and reacts to the real mouse).
 */
export function HeroDataViz() {
  const ref = React.useRef<HTMLDivElement>(null);

  // Normalised pointer offset (-0.5..0.5) feeding card parallax.
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const px = useSpring(mx, { stiffness: 60, damping: 18 });
  const py = useSpring(my, { stiffness: 60, damping: 18 });

  // Spring-physics cursor position (in % of the box).
  const cxRaw = useMotionValue(50);
  const cyRaw = useMotionValue(46);
  const cx = useSpring(cxRaw, { stiffness: 120, damping: 14, mass: 0.6 });
  const cy = useSpring(cyRaw, { stiffness: 120, damping: 14, mass: 0.6 });

  const [hovering, setHovering] = React.useState(false);
  const [tap, setTap] = React.useState(false);

  // Scripted tour the cursor follows when the user isn't driving it.
  const tour = React.useMemo(
    () => [
      { x: 24, y: 30 },
      { x: 70, y: 22 },
      { x: 78, y: 64 },
      { x: 34, y: 72 },
      { x: 50, y: 46 },
    ],
    [],
  );

  React.useEffect(() => {
    if (hovering) return;
    let i = 0;
    cxRaw.set(tour[0].x);
    cyRaw.set(tour[0].y);
    const tick = () => {
      i = (i + 1) % tour.length;
      cxRaw.set(tour[i].x);
      cyRaw.set(tour[i].y);
      setTap(true);
      window.setTimeout(() => setTap(false), 260);
    };
    const id = window.setInterval(tick, 1700);
    return () => window.clearInterval(id);
  }, [hovering, tour, cxRaw, cyRaw]);

  const onMove = (e: React.MouseEvent) => {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect) return;
    const nx = (e.clientX - rect.left) / rect.width;
    const ny = (e.clientY - rect.top) / rect.height;
    mx.set(nx - 0.5);
    my.set(ny - 0.5);
    cxRaw.set(nx * 100);
    cyRaw.set(ny * 100);
  };

  const onLeave = () => {
    setHovering(false);
    mx.set(0);
    my.set(0);
  };

  return (
    <div
      ref={ref}
      onMouseEnter={() => setHovering(true)}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      className="relative h-[380px] w-full max-w-[520px] sm:h-[460px] lg:w-[520px] lg:max-w-none"
    >
      {/* Aurora glow backdrop */}
      <motion.div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(closest-side at 50% 45%, rgba(199,240,224,0.55), rgba(201,216,255,0.45) 45%, rgba(230,201,245,0.35) 70%, transparent 78%)",
        }}
        animate={{ scale: [1, 1.06, 1], opacity: [0.9, 1, 0.9] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Soft floating glass mark behind the cards */}
      <motion.div
        className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 opacity-60"
        animate={{ rotate: [0, 12, 0], y: [0, -10, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        style={{ x: useTransform(px, (v) => v * 12), y: useTransform(py, (v) => v * 12) }}
      >
        <SynthMark className="h-44 w-44 text-violet-300/50 sm:h-56 sm:w-56" />
      </motion.div>

      {/* Drifting particles */}
      {[
        { x: "12%", y: "18%", s: 8, c: "#a78bfa", d: 5 },
        { x: "86%", y: "30%", s: 6, c: "#5b8c5a", d: 6.5 },
        { x: "20%", y: "82%", s: 7, c: "#d06b9c", d: 5.8 },
        { x: "70%", y: "84%", s: 5, c: "#6d5bd0", d: 7 },
        { x: "92%", y: "60%", s: 9, c: "#7aa2f7", d: 6 },
      ].map((p, i) => (
        <motion.span
          key={i}
          className="pointer-events-none absolute rounded-full"
          style={{ left: p.x, top: p.y, width: p.s, height: p.s, background: p.c, opacity: 0.6 }}
          animate={{ y: [0, -18, 0], opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: p.d, repeat: Infinity, ease: "easeInOut", delay: i * 0.4 }}
        />
      ))}

      {/* Card: trend line */}
      <FloatCard px={px} py={py} depth={1.2} delay={0.2} className="left-[2%] top-[10%] w-[190px] p-4">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-[11px] font-semibold text-neutral-500">Revenue</span>
          <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-500">
            <TrendingUp className="h-3 w-3" /> 24%
          </span>
        </div>
        <MiniLine accent="#6d5bd0" />
      </FloatCard>

      {/* Card: bars */}
      <FloatCard px={px} py={py} depth={0.7} delay={0.6} className="right-[4%] top-[4%] w-[150px] p-4">
        <span className="text-[11px] font-semibold text-neutral-500">Weekly</span>
        <div className="mt-2">
          <MiniBars accent="#5b8c5a" />
        </div>
      </FloatCard>

      {/* Card: donut + label */}
      <FloatCard
        px={px}
        py={py}
        depth={1.5}
        delay={0.9}
        className="bottom-[8%] left-[6%] flex w-[180px] items-center gap-3 p-4"
      >
        <MiniDonut accent="#d06b9c" />
        <div>
          <div className="text-[20px] font-extrabold leading-none text-neutral-900">68%</div>
          <span className="text-[11px] text-neutral-500">Accuracy</span>
        </div>
      </FloatCard>

      {/* Card: KPI pill */}
      <FloatCard
        px={px}
        py={py}
        depth={0.9}
        delay={1.2}
        className="bottom-[18%] right-[2%] w-[150px] p-4"
      >
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-violet-100">
            <Activity className="h-4 w-4 text-violet-600" />
          </span>
          <div>
            <div className="text-[16px] font-extrabold leading-none text-neutral-900">1,284</div>
            <span className="text-[10px] text-neutral-500">Charts made</span>
          </div>
        </div>
      </FloatCard>

      {/* Card: scatter dots */}
      <FloatCard
        px={px}
        py={py}
        depth={1.8}
        delay={0.4}
        className="left-[42%] top-[40%] h-[78px] w-[110px] p-3"
      >
        <svg viewBox="0 0 100 60" className="h-full w-full">
          {[
            [12, 44, "#6d5bd0"],
            [30, 20, "#5b8c5a"],
            [48, 36, "#d06b9c"],
            [66, 14, "#7aa2f7"],
            [82, 30, "#6d5bd0"],
            [22, 50, "#d06b9c"],
            [74, 46, "#5b8c5a"],
          ].map(([x, y, c], i) => (
            <motion.circle
              key={i}
              cx={x as number}
              cy={y as number}
              r="5"
              fill={c as string}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5 + i * 0.08, type: "spring", stiffness: 300 }}
            />
          ))}
        </svg>
      </FloatCard>

      {/* Spring-physics cursor */}
      <motion.div
        className="pointer-events-none absolute z-30"
        style={{ left: useTransform(cx, (v) => `${v}%`), top: useTransform(cy, (v) => `${v}%`) }}
      >
        <motion.div animate={{ scale: tap ? 0.8 : 1 }} transition={{ type: "spring", stiffness: 400, damping: 15 }}>
          {/* click ripple */}
          {tap && (
            <motion.span
              className="absolute -left-1 -top-1 h-7 w-7 rounded-full border-2 border-violet-400"
              initial={{ scale: 0.4, opacity: 0.8 }}
              animate={{ scale: 1.8, opacity: 0 }}
              transition={{ duration: 0.5 }}
            />
          )}
          <MousePointer2 className="h-6 w-6 text-neutral-900 drop-shadow-md" style={{ fill: "#1a1a1a" }} />
        </motion.div>
      </motion.div>
    </div>
  );
}

/** Iridescent glass asterisk shape for the hero, with a slow float. */
export function HeroGlassMark() {
  return (
    <motion.div
      className="relative flex items-center justify-center"
      animate={{ y: [0, -16, 0], rotate: [0, 4, 0] }}
      transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
    >
      <svg viewBox="0 0 400 400" className="h-[300px] w-[300px] sm:h-[420px] sm:w-[420px]">
        <defs>
          <radialGradient id="glassG" cx="38%" cy="32%" r="75%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
            <stop offset="35%" stopColor="#c7f0e0" stopOpacity="0.85" />
            <stop offset="60%" stopColor="#c9d8ff" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#e6c9f5" stopOpacity="0.75" />
          </radialGradient>
          <filter id="glassBlur" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" />
          </filter>
        </defs>
        <g filter="url(#glassBlur)">
          <path
            transform="translate(200,200) scale(11)"
            d="M0-15c.7 0 1.2.5 1.2 1.2v7l5-5a1.3 1.3 0 1 1 1.8 1.8l-5 5h7a1.2 1.2 0 0 1 0 2.4h-7l5 5a1.3 1.3 0 1 1-1.8 1.8l-5-5v7a1.2 1.2 0 0 1-2.4 0v-7l-5 5a1.3 1.3 0 1 1-1.8-1.8l5-5h-7a1.2 1.2 0 0 1 0-2.4h7l-5-5a1.3 1.3 0 1 1 1.8-1.8l5 5v-7c0-.7.5-1.2 1.2-1.2z"
            fill="url(#glassG)"
            stroke="#ffffff"
            strokeWidth="0.4"
          />
        </g>
      </svg>
    </motion.div>
  );
}
