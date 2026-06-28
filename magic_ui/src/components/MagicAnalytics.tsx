import React from "react";
import { motion } from "framer-motion";
import {
  Activity,
  BarChart3,
  Clock,
  Database,
  Gauge,
  MousePointer2,
  PieChart,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react";
import { MagicCard } from "./ui/magic-card";
import { PageShell } from "./ui/page-shell";
import NumberTicker from "./ui/number-ticker";
import { VisualStatsLogo } from "./ui/synth-visuals";

interface ChartTypeItem {
  viz_type: string;
  count: number;
}

interface MagicAnalyticsProps {
  totalUsers?: number;
  totalVisualizations?: number;
  totalDatasets?: number;
  totalInteractions?: number;
  avgSessionDuration?: string;
  topChartTypes?: ChartTypeItem[];
  topActions?: { action_type: string; count: number }[];
}

const MagicAnalytics: React.FC<MagicAnalyticsProps> = ({
  totalUsers = 0,
  totalVisualizations = 0,
  totalDatasets = 0,
  totalInteractions = 0,
  avgSessionDuration = "—",
  topChartTypes = [],
}) => {
  const totalActivity = totalVisualizations + totalDatasets + totalInteractions;
  const platformScore = Math.min(100, Math.round((totalUsers > 0 ? 35 : 0) + (totalDatasets > 0 ? 20 : 0) + (totalVisualizations > 0 ? 25 : 0) + (totalInteractions > 0 ? 20 : 0)));
  const conversionRate = totalDatasets > 0 ? Math.round((totalVisualizations / totalDatasets) * 100) : 0;
  const metrics = [
    {
      label: "Total users",
      value: totalUsers,
      icon: Users,
      color: "text-blue-600",
      bg: "bg-blue-50",
      note: "Registered accounts",
      accent: "#3b82f6",
    },
    {
      label: "Visualizations",
      value: totalVisualizations,
      icon: BarChart3,
      color: "text-violet-600",
      bg: "bg-violet-50",
      note: "Generated + evaluated",
      accent: "#6d5bd0",
    },
    {
      label: "Datasets",
      value: totalDatasets,
      icon: Database,
      color: "text-amber-600",
      bg: "bg-amber-50",
      note: "Uploaded sources",
      accent: "#d6a247",
    },
    {
      label: "Interactions",
      value: totalInteractions,
      icon: Activity,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      note: "Tracked actions",
      accent: "#5b8c5a",
    },
  ];

  const maxChartCount = Math.max(...topChartTypes.map((c) => c.count), 1);
  const activityBars = [38, 64, 48, 76, 54, 88, 68, 92, 58, 82, 70, 96];

  return (
    <PageShell>
      <div className="relative mb-6 overflow-hidden rounded-[30px] border border-black/5 bg-white/80 p-5 shadow-[0_18px_60px_rgba(80,70,160,0.10)] backdrop-blur sm:p-7">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(680px 340px at 86% 0%, rgba(109,91,208,0.18), transparent 70%), radial-gradient(520px 280px at 8% 96%, rgba(91,140,90,0.16), transparent 70%)",
          }}
        />
        <motion.div
          className="pointer-events-none absolute right-10 top-8 opacity-20"
          animate={{ rotate: [0, 8, 0], y: [0, -8, 0] }}
          transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
        >
          <VisualStatsLogo className="h-32 w-32 text-violet-500" />
        </motion.div>

        <div className="relative grid grid-cols-1 items-center gap-6 lg:grid-cols-[1fr_430px]">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 inline-flex items-center gap-2 rounded-full border border-black/5 bg-white/80 px-3.5 py-2 text-[11px] uppercase tracking-[0.16em] text-neutral-500 shadow-sm"
              style={{ fontFamily: "var(--font-mono)" }}
            >
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
              Admin Quality Analytics
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="max-w-[760px] text-[34px] font-extrabold leading-tight tracking-[-0.055em] text-neutral-950 sm:text-[48px]"
            >
              Platform health, usage quality, and user activity in one clean view.
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mt-4 max-w-2xl text-[15px] leading-relaxed text-neutral-500"
            >
              Review who is using VisualStats, how often charts are generated or evaluated, and where activity is concentrated.
            </motion.p>

            <div className="mt-6 grid max-w-2xl grid-cols-1 gap-3 sm:grid-cols-3">
              <HeroStat icon={<Gauge className="h-4 w-4" />} label="Health score" value={`${platformScore}%`} />
              <HeroStat icon={<Clock className="h-4 w-4" />} label="Avg session" value={avgSessionDuration} />
              <HeroStat icon={<TrendingUp className="h-4 w-4" />} label="Viz per dataset" value={conversionRate ? `${conversionRate}%` : "—"} />
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96, x: 16 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ delay: 0.16 }}
            className="relative overflow-hidden rounded-[26px] border border-black/5 bg-neutral-950 p-5 text-white shadow-[0_20px_60px_rgba(17,24,39,0.18)]"
          >
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "radial-gradient(320px 180px at 80% 10%, rgba(167,139,250,0.35), transparent 70%), radial-gradient(260px 180px at 8% 90%, rgba(91,140,90,0.28), transparent 70%)",
              }}
            />
            <div className="relative">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <p className="text-[11px] uppercase tracking-[0.16em] text-white/45">Live activity</p>
                  <p className="mt-1 text-2xl font-extrabold tracking-tight">{totalActivity}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/10 p-3">
                  <Sparkles className="h-5 w-5 text-emerald-300" />
                </div>
              </div>

              <div className="mb-5 flex h-32 items-end gap-2 rounded-2xl border border-white/10 bg-white/[0.06] p-3">
                {activityBars.map((height, i) => (
                  <motion.div
                    key={i}
                    className="flex-1 rounded-t-lg bg-gradient-to-t from-[#5b8c5a] to-[#a78bfa]"
                    initial={{ height: 0, opacity: 0.5 }}
                    animate={{ height: `${height}%`, opacity: 1 }}
                    transition={{ delay: 0.25 + i * 0.04, duration: 0.75, ease: "easeOut" }}
                  />
                ))}
              </div>

              <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-white/70">
                  <MousePointer2 className="h-4 w-4 text-violet-300" />
                  Admin insight stream
                </div>
                <span className="rounded-full bg-emerald-300/15 px-3 py-1 text-xs font-bold text-emerald-200">
                  Synced
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {metrics.map((m, i) => (
          <MagicCard key={m.label} gradientColor={`${m.accent}22`} className="relative overflow-hidden border-black/5 bg-white/90">
            <motion.div
              className="absolute -right-8 -top-8 h-24 w-24 rounded-full opacity-10 blur-2xl"
              style={{ background: m.accent }}
              animate={{ scale: [1, 1.15, 1] }}
              transition={{ duration: 3 + i, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <div className="mb-4 flex items-start justify-between gap-3">
                <div className={`inline-flex rounded-2xl p-3 ${m.bg}`}>
                  <m.icon className={`h-5 w-5 ${m.color}`} />
                </div>
                <span className="rounded-full border border-black/5 bg-neutral-50 px-2.5 py-1 text-[11px] font-bold uppercase tracking-[0.12em] text-neutral-400">
                  Live
                </span>
              </div>
              <p className="text-sm font-medium text-neutral-500">{m.label}</p>
              <p className="mt-1 text-3xl font-extrabold tracking-tight text-neutral-950">
                <NumberTicker value={m.value} />
              </p>
              <p className="mt-2 text-xs font-medium text-neutral-400">{m.note}</p>
            </motion.div>
          </MagicCard>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-5">
        <MagicCard className="border-black/5" gradientColor="rgba(109,91,208,0.14)">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <div className="mb-1 flex items-center gap-2 text-[11px] uppercase tracking-[0.14em] text-neutral-400">
                <BarChart3 className="h-3.5 w-3.5 text-violet-600" />
                Distribution
              </div>
              <h2 className="text-xl font-extrabold text-neutral-950">Top chart types</h2>
              <p className="mt-1 text-sm text-neutral-500">Which visualization formats users rely on most.</p>
            </div>
            <PieChart className="h-5 w-5 text-violet-500" />
          </div>
          {topChartTypes.length > 0 ? (
            <div className="grid grid-cols-1 gap-x-8 gap-y-5 md:grid-cols-2">
              {topChartTypes.map((item, i) => (
                <div key={item.viz_type} className="rounded-2xl border border-black/5 bg-neutral-50/70 p-4">
                  <div className="mb-1.5 flex justify-between text-sm">
                    <span className="font-medium capitalize text-neutral-700">{item.viz_type}</span>
                    <span className="font-semibold text-violet-600">{item.count}</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded-full bg-neutral-100">
                    <motion.div
                      className="h-full rounded-full bg-gradient-to-r from-[#6d5bd0] to-[#a78bfa]"
                      initial={{ width: 0 }}
                      whileInView={{ width: `${(item.count / maxChartCount) * 100}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.7, delay: i * 0.08 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="rounded-xl border border-dashed border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-400">
              No chart data yet.
            </p>
          )}
        </MagicCard>
      </div>
    </PageShell>
  );
};

function HeroStat({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.18 }}
      className="rounded-2xl border border-black/5 bg-white/70 px-4 py-3 shadow-sm"
    >
      <div className="mb-2 flex items-center gap-2 text-[11px] uppercase tracking-[0.14em] text-neutral-400">
        <span className="text-violet-600">{icon}</span>
        {label}
      </div>
      <p className="text-lg font-extrabold tracking-tight text-neutral-950">{value}</p>
    </motion.div>
  );
}

export default MagicAnalytics;
