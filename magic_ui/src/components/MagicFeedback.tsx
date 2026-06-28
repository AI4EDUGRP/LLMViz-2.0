import React from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle2,
  Gauge,
  Lightbulb,
  ListChecks,
  ScanLine,
  Sparkles,
  Target,
} from "lucide-react";
import { MagicCard } from "./ui/magic-card";

export const BorderBeam = ({
  className,
  size = 200,
  duration = 15,
  anchor = 90,
  borderWidth = 1.5,
  colorFrom = "#3B82F6",
  colorTo = "#1E40AF",
  delay = 0,
}: {
  className?: string;
  size?: number;
  duration?: number;
  borderWidth?: number;
  anchor?: number;
  colorFrom?: string;
  colorTo?: string;
  delay?: number;
}) => {
  return (
    <div
      style={
        {
          "--size": size,
          "--duration": duration,
          "--anchor": anchor,
          "--border-width": borderWidth,
          "--color-from": colorFrom,
          "--color-to": colorTo,
          "--delay": `-${delay}s`,
        } as React.CSSProperties
      }
      className={`pointer-events-none absolute inset-0 rounded-[inherit] [border:calc(var(--border-width)*1px)_solid_transparent] 
        ![mask-clip:padding-box,border-box] ![mask-composite:intersect] [mask:linear-gradient(transparent,transparent),linear-gradient(white,white)]
        after:absolute after:aspect-square after:w-[calc(var(--size)*1px)] after:animate-border-beam after:[animation-delay:var(--delay)] 
        after:[background:linear-gradient(to_left,var(--color-from),var(--color-to),transparent)] after:[offset-anchor:calc(var(--anchor)*1%)_50%] 
        after:[offset-path:rect(0_auto_auto_0_round_calc(var(--size)*1px))] ${className}`}
    />
  );
};

interface MagicFeedbackProps {
  feedback: string;
}

function cleanLine(line: string) {
  return line
    .replace(/^#{1,6}\s*/, "")
    .replace(/^[-*]\s*/, "")
    .replace(/\*\*/g, "")
    .trim();
}

function getSection(lines: string[], heading: string) {
  const start = lines.findIndex((line) => cleanLine(line).toLowerCase() === heading.toLowerCase());
  if (start < 0) return [];

  const end = lines.findIndex((line, index) => {
    if (index <= start) return false;
    const cleaned = cleanLine(line);
    return /^(summary|strengths|issues|recommendations|checklist|overall score):?$/i.test(cleaned);
  });

  return lines
    .slice(start + 1, end > -1 ? end : undefined)
    .map(cleanLine)
    .filter(Boolean);
}

function fallbackItems(lines: string[], keywords: string[], limit = 3) {
  return lines
    .map(cleanLine)
    .filter((line) => keywords.some((keyword) => line.toLowerCase().includes(keyword)))
    .slice(0, limit);
}

const MagicFeedback: React.FC<MagicFeedbackProps> = ({ feedback }) => {
  const rawLines = feedback
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
  const cleanedLines = rawLines.map(cleanLine).filter(Boolean);

  const scoreMatch = feedback.match(/overall score:\s*(\d{1,3})\s*\/\s*100/i) || feedback.match(/(\d{1,3})\s*\/\s*100/);
  const score = Math.min(100, Math.max(0, scoreMatch ? Number(scoreMatch[1]) : 0));
  const scoreLabel = score ? `${score}/100` : "Reviewed";

  const summary = getSection(rawLines, "SUMMARY:").join(" ") || cleanedLines[0] || "The evaluator reviewed the uploaded visualization.";
  const strengths = getSection(rawLines, "STRENGTHS:").slice(0, 4);
  const parsedIssues = getSection(rawLines, "ISSUES:").slice(0, 4);
  const parsedRecommendations = getSection(rawLines, "RECOMMENDATIONS:").slice(0, 4);
  const issues = parsedIssues.length
    ? parsedIssues
    : fallbackItems(cleanedLines, ["missing", "not ", "cropped", "unclear", "issue"], 4);
  const recommendations = parsedRecommendations.length
    ? parsedRecommendations
    : fallbackItems(cleanedLines, ["recommend", "should", "improve", "consider"], 4);
  const checklist = getSection(rawLines, "CHECKLIST:").slice(0, 8);
  const scoreColor = score >= 80 ? "#5b8c5a" : score >= 60 ? "#d6a247" : "#d06b6b";

  return (
    <MagicCard
      className="relative overflow-hidden border-black/5 bg-white/90"
      gradientColor="rgba(91,140,90,0.16)"
    >
      <BorderBeam size={280} duration={8} delay={0} colorFrom="#5b8c5a" colorTo="#a78bfa" />
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(520px 260px at 88% 0%, rgba(91,140,90,0.12), transparent 70%)",
        }}
      />

      <div className="relative" style={{ fontFamily: "var(--font-body)" }}>
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <motion.div
              className="rounded-2xl bg-emerald-50 p-3.5"
              animate={{ scale: [1, 1.06, 1] }}
              transition={{ duration: 2.5, repeat: Infinity }}
            >
              <Sparkles className="h-6 w-6 text-emerald-600" />
            </motion.div>
            <div>
              <div className="flex items-center gap-2 text-[12px] font-semibold uppercase tracking-[0.16em] text-neutral-500">
                <ScanLine className="h-3.5 w-3.5 text-emerald-600" />
                Evaluation Complete
              </div>
              <h4 className="mt-1 text-[26px] font-bold tracking-[-0.035em] text-neutral-950" style={{ fontFamily: "var(--font-display)" }}>
                Visualization Quality Analysis
              </h4>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-2xl border border-black/5 bg-white px-5 py-4 shadow-sm">
            <div className="relative flex h-14 w-14 items-center justify-center">
              <svg viewBox="0 0 64 64" className="-rotate-90">
                <circle cx="32" cy="32" r="26" fill="none" stroke="#00000010" strokeWidth="7" />
                <motion.circle
                  cx="32"
                  cy="32"
                  r="26"
                  fill="none"
                  stroke={scoreColor}
                  strokeWidth="7"
                  strokeLinecap="round"
                  strokeDasharray={163.36}
                  initial={{ strokeDashoffset: 163.36 }}
                  animate={{ strokeDashoffset: score ? 163.36 * (1 - score / 100) : 0 }}
                  transition={{ duration: 1, ease: "easeOut" }}
                />
              </svg>
              <Gauge className="absolute h-5 w-5" style={{ color: scoreColor }} />
            </div>
            <div>
              <p className="text-[12px] font-semibold uppercase tracking-[0.14em] text-neutral-500">Quality score</p>
              <p className="text-[22px] font-bold text-neutral-950" style={{ fontFamily: "var(--font-display)" }}>{scoreLabel}</p>
            </div>
          </div>
        </div>

        <div className="mb-5 rounded-[22px] border border-black/5 bg-neutral-50 p-5 shadow-sm">
          <div className="mb-3 flex items-center gap-2 text-[16px] font-bold text-neutral-950" style={{ fontFamily: "var(--font-display)" }}>
            <Target className="h-5 w-5 text-violet-600" />
            AI Summary
          </div>
          <p className="text-[16px] leading-8 text-neutral-700">{summary}</p>
        </div>

        <div className="mb-5 grid grid-cols-1 gap-4 lg:grid-cols-3">
          <ReportList
            title="Strengths"
            icon={<CheckCircle2 className="h-5 w-5 text-emerald-600" />}
            items={strengths.length ? strengths : ["The chart was successfully readable enough for analysis."]}
          />
          <ReportList
            title="Issues"
            icon={<AlertTriangle className="h-5 w-5 text-amber-600" />}
            items={issues.length ? issues : ["No major issue found in the uploaded chart."]}
          />
          <ReportList
            title="Recommendations"
            icon={<Lightbulb className="h-5 w-5 text-violet-600" />}
            items={recommendations.length ? recommendations : ["Keep labels clear, legends visible, and layout uncluttered."]}
          />
        </div>

        {checklist.length > 0 && (
          <div className="mb-5 rounded-[22px] border border-black/5 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2 text-[16px] font-bold text-neutral-950" style={{ fontFamily: "var(--font-display)" }}>
              <ListChecks className="h-5 w-5 text-emerald-600" />
              Quality checklist
            </div>
            <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
              {checklist.map((item, i) => {
                const pass = /pass/i.test(item) && !/needs work/i.test(item);
                return (
                  <motion.div
                    key={`${item}-${i}`}
                    initial={{ opacity: 0, y: 8 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.04 }}
                    className="rounded-xl border border-black/5 bg-neutral-50 px-3.5 py-2.5 text-[14px] leading-6 text-neutral-700"
                  >
                    <span className={pass ? "font-semibold text-emerald-700" : "font-semibold text-amber-700"}>
                      {pass ? "Pass" : "Needs review"}
                    </span>{" "}
                    {item.replace(/pass|needs work/gi, "").replace(/^[-:\s]+/, "")}
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        <div className="rounded-[22px] border border-black/5 bg-white p-5 shadow-sm">
          <details>
            <summary className="cursor-pointer text-[16px] font-bold text-neutral-950" style={{ fontFamily: "var(--font-display)" }}>
              Full AI report
            </summary>
            <p className="mt-4 max-h-[360px] overflow-auto whitespace-pre-wrap text-[15px] leading-7 text-neutral-700">
              {feedback.replace(/\*\*/g, "")}
            </p>
          </details>
        </div>
      </div>
    </MagicCard>
  );
};

function ReportList({
  title,
  icon,
  items,
}: {
  title: string;
  icon: React.ReactNode;
  items: string[];
}) {
  return (
    <div className="rounded-[22px] border border-black/5 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center gap-2 text-[16px] font-bold text-neutral-950" style={{ fontFamily: "var(--font-display)" }}>
        {icon}
        {title}
      </div>
      <ul className="space-y-2.5">
        {items.map((item, i) => (
          <li key={`${item}-${i}`} className="text-[15px] leading-7 text-neutral-700">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MagicFeedback;
