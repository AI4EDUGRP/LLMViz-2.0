import React, { useCallback, useState } from "react";
import { Streamlit } from "streamlit-component-lib";
import { motion } from "framer-motion";
import {
  ArrowUpRight,
  Workflow,
  Boxes,
  Bot,
  BarChart3,
  Sparkles,
  Plus,
  Minus,
  LogOut,
} from "lucide-react";
import NumberTicker from "./ui/number-ticker";
import {
  ChatMockup,
  AnalyzeVisual,
  AssistNetwork,
  VisualStatsLogo,
  HeroDataViz,
  GeneratorShowcase,
  EvaluatorShowcase,
} from "./ui/synth-visuals";
import StackingFeatureCards, { type FeatureRowData } from "./ui/stacking-feature-cards";

interface DatasetItem {
  dataset_name?: string;
}
interface SessionItem {
  user_query?: string;
}
interface VizItem {
  viz_type?: string;
}
interface ChartTypeItem {
  viz_type: string;
  count: number;
}

interface MagicDashboardProps {
  isAdmin?: boolean;
  username?: string;
  datasets?: DatasetItem[];
  sessions?: SessionItem[];
  visualizations?: VizItem[];
  stats?: { datasets: number; sessions: number; visualizations: number; users?: number; interactions?: number };
  chartTypes?: ChartTypeItem[];
  supportedCharts?: string[];
}

const SYNTH = "var(--font-synth)";
const MONO = "var(--font-mono)";

const fade = {
  hidden: { opacity: 0, y: 24 },
  show: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.06, duration: 0.55, ease: "easeOut" as const },
  }),
};

/** Uppercase mono eyebrow label with optional leading icon. */
function Eyebrow({
  icon: Icon,
  children,
}: {
  icon?: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <span
      className="inline-flex items-center gap-2 text-[12px] uppercase tracking-[0.18em] text-neutral-500"
      style={{ fontFamily: MONO }}
    >
      {Icon ? <Icon className="h-3.5 w-3.5 text-neutral-700" /> : null}
      {children}
    </span>
  );
}

function PrimaryBtn({
  onClick,
  children,
  full = false,
}: {
  onClick: () => void;
  children: React.ReactNode;
  full?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`group inline-flex items-center justify-center gap-2 rounded-xl bg-neutral-900 px-6 py-3.5 text-[13px] uppercase tracking-[0.12em] text-white transition-all hover:bg-neutral-800 ${full ? "w-full" : ""}`}
      style={{ fontFamily: MONO }}
    >
      {children}
    </button>
  );
}

function GhostBtn({ onClick, children }: { onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center justify-center gap-2 rounded-xl border border-neutral-300 bg-white px-6 py-3.5 text-[13px] uppercase tracking-[0.12em] text-neutral-900 transition-colors hover:bg-neutral-50"
      style={{ fontFamily: MONO }}
    >
      {children}
    </button>
  );
}

const MagicDashboard: React.FC<MagicDashboardProps> = ({
  isAdmin = false,
  username = "there",
  datasets = [],
  sessions = [],
  visualizations = [],
  stats,
  chartTypes = [],
  supportedCharts = [],
}) => {
  const nav = useCallback((target: string) => {
    Streamlit.setComponentValue({ action: "navigate", target, timestamp: Date.now() });
  }, []);
  const logout = useCallback(() => {
    Streamlit.setComponentValue({ action: "logout", timestamp: Date.now() });
  }, []);
  const scrollToSection = useCallback((target: string) => {
    document.getElementById(target)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);
  const handleFooterLink = useCallback(
    (target?: string) => {
      if (!target) return;
      if (target === "logout") {
        logout();
      } else if (target === "capabilities" || target === "faq") {
        scrollToSection(target);
      } else {
        nav(target);
      }
    },
    [logout, nav, scrollToSection],
  );

  const datasetCount = stats?.datasets ?? datasets.length;
  const sessionCount = stats?.sessions ?? sessions.length;
  const vizCount = stats?.visualizations ?? visualizations.length;
  const userCount = stats?.users ?? 0;
  const interactionCount = stats?.interactions ?? sessionCount;
  const maxChart = Math.max(...chartTypes.map((c) => c.count), 1);

  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const navLinks = [
    { label: "Generator", onClick: () => nav("viz_generator") },
    { label: "Evaluator", onClick: () => nav("viz_evaluator") },
    ...(isAdmin ? [{ label: "Analytics", onClick: () => nav("analytics_dashboard") }] : []),
    { label: "Capabilities", onClick: () => scrollToSection("capabilities") },
  ];

  // Alternating coloured capability rows (mirrors SynthAI Automation / Analytics / Assistant).
  const featureRows: FeatureRowData[] = [
    {
      tag: "GENERATION",
      icon: Workflow,
      accent: "#5b8c5a",
      panel: "linear-gradient(135deg,#eef4ea 0%,#e3efdc 100%)",
      title: "Generate charts from data",
      body: "Eliminate manual chart building. Upload a dataset, describe what you want in plain English, and let the assistant produce the right visualization automatically.",
      visual: "chat" as const,
    },
    {
      tag: "ANALYTICS",
      icon: BarChart3,
      accent: "#6d5bd0",
      panel: "linear-gradient(135deg,#efecf9 0%,#e6e1f6 100%)",
      title: "Analyze business performance",
      body: "Surface trends and outliers instantly. The assistant reviews your data, highlights what matters, and turns raw numbers into clear, decision-ready visuals.",
      visual: "analyze" as const,
    },
    {
      tag: "AI ASSISTANT",
      icon: Bot,
      accent: "#d06b9c",
      panel: "linear-gradient(135deg,#f8ecf2 0%,#f6e2ec 100%)",
      title: "Assist your team and customers",
      body: "Refine visualizations through conversation. Adjust chart types, filters, and styling without writing a single line of code — your whole team can explore data.",
      visual: "network" as const,
    },
  ];

  const stat = [
    { label: "Total users", value: userCount },
    { label: "Visualizations", value: vizCount },
    { label: "Datasets", value: datasetCount },
    { label: "Interactions", value: interactionCount },
  ];

  const faqs = [
    {
      q: "What does VisualStats do?",
      a: "It turns raw datasets into clear visualizations using AI, and evaluates the quality of existing charts — all through a conversational interface.",
    },
    {
      q: "What file formats can I upload?",
      a: "CSV, Excel (XLSX/XLS), JSON, XML, and plain text files are all supported in the Viz Generator.",
    },
    {
      q: "What chart types are supported?",
      a: `We produce ${supportedCharts.length || "many"} chart types including bar, line, scatter, pie, histogram, heatmap, box plots, and more.`,
    },
    {
      q: "How does the Viz Evaluator work?",
      a: "Upload a chart image and our AI reviews labels, color usage, clarity, and effectiveness, then returns actionable feedback.",
    },
    {
      q: "Is my data saved?",
      a: "Datasets, queries, and generated charts are stored securely in Supabase for your account. Guest sessions are not permanently saved.",
    },
  ];

  return (
    <div className="w-full bg-[#fbfbfa] text-neutral-900" style={{ fontFamily: SYNTH }}>
      {/* ===== Hero with soft iridescent gradient ===== */}
      <div className="relative overflow-hidden">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(900px 520px at 88% 8%, #e7ddf7 0%, #dfe8fb 30%, #e3f3ec 52%, transparent 72%)",
          }}
        />

        <div className="relative mx-auto w-full px-6 sm:px-10 lg:px-16 xl:px-20">
          {/* Navbar pill */}
          <nav className="flex min-h-[64px] items-center justify-between pt-8">
            <div className="flex items-center gap-3">
              <VisualStatsLogo className="h-10 w-10" />
              <span className="text-[20px] font-bold tracking-tight">VisualStats</span>
            </div>
            <div className="hidden items-center gap-1.5 rounded-2xl border border-black/5 bg-white/85 px-3 py-2 shadow-[0_10px_34px_rgba(0,0,0,0.07)] backdrop-blur md:flex">
              {navLinks.map((l) => (
                <button
                  type="button"
                  key={l.label}
                  onClick={l.onClick}
                  className="rounded-xl px-4 py-2 text-[13px] uppercase tracking-[0.1em] text-neutral-600 transition-colors hover:bg-neutral-100 hover:text-neutral-900"
                  style={{ fontFamily: MONO }}
                >
                  {l.label}
                </button>
              ))}
              <button
                type="button"
                onClick={logout}
                className="ml-1 inline-flex items-center gap-1.5 rounded-xl px-4 py-2.5 text-[13px] uppercase tracking-[0.1em] text-neutral-500 transition-colors hover:bg-red-50 hover:text-red-600"
                style={{ fontFamily: MONO }}
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
            <button
              type="button"
              onClick={logout}
              className="rounded-xl bg-neutral-900 px-5 py-2.5 text-[13px] uppercase tracking-[0.1em] text-white md:hidden"
              style={{ fontFamily: MONO }}
            >
              Logout
            </button>
          </nav>

          {/* Hero content */}
          <div className="grid grid-cols-1 items-center gap-10 py-20 sm:py-28 lg:grid-cols-2 lg:gap-12">
            <motion.div variants={fade} initial="hidden" animate="show">
              <Eyebrow icon={Sparkles}>AI Data Visualization Platform</Eyebrow>
              <h1 className="mt-7 max-w-[680px] text-[52px] font-extrabold leading-[1.03] tracking-tight sm:text-[72px]">
                Your Intelligent Assistant for Data Insight
              </h1>
              <p className="mt-7 max-w-[520px] text-[18px] leading-relaxed text-neutral-500 sm:text-[20px]">
                Welcome back, {username}. Upload datasets, generate charts through conversation, and
                evaluate visualization quality — all in one powerful AI workspace.
              </p>
              <div className="mt-10 flex flex-wrap items-center gap-4">
                <PrimaryBtn onClick={() => nav("viz_generator")}>
                  Start Now <ArrowUpRight className="h-4 w-4" />
                </PrimaryBtn>
                <GhostBtn onClick={() => nav("viz_evaluator")}>View Demo</GhostBtn>
              </div>
            </motion.div>

            <motion.div
              variants={fade}
              initial="hidden"
              animate="show"
              className="relative flex justify-center lg:justify-center"
            >
              <div className="origin-center">
                <HeroDataViz />
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <div className="mx-auto w-full px-6 sm:px-10 lg:px-16 xl:px-20">
        {/* ===== Capabilities intro ===== */}
        <section id="capabilities" className="scroll-mt-10 pb-12 pt-14 text-center sm:pt-16">
          <div className="flex justify-center">
            <Eyebrow icon={Boxes}>Platform Capabilities</Eyebrow>
          </div>
          <h2 className="mx-auto mt-6 max-w-[860px] text-[30px] font-bold leading-[1.25] tracking-tight text-neutral-400 sm:text-[44px]">
            A flexible AI platform designed to{" "}
            <InlineWord color="#5b8c5a" icon={Workflow}>
              <span className="text-neutral-900">generate charts</span>
            </InlineWord>{" "}
            <span className="text-neutral-900">evaluate quality</span>{" "}
            <InlineWord color="#6d5bd0" icon={BarChart3} />
            and{" "}
            <InlineWord color="#d06b9c" icon={Bot}>
              <span className="text-neutral-900">refine</span>
            </InlineWord>{" "}
            your data effortlessly.
          </h2>
        </section>

        {/* ===== Feature rows — sticky stack scroll ===== */}
        <StackingFeatureCards
          rows={featureRows}
          monoFont={MONO}
          onLearnMore={() => nav("viz_generator")}
          renderEyebrow={(Icon, children) => <Eyebrow icon={Icon}>{children}</Eyebrow>}
          renderVisual={(visual, accent) => {
            if (visual === "chat") return <ChatMockup accent={accent} />;
            if (visual === "analyze") return <AnalyzeVisual accent={accent} />;
            return <AssistNetwork accent={accent} />;
          }}
        />

        {/* ===== Stats band ===== */}
        <motion.section
          variants={fade}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="my-16 grid grid-cols-2 gap-4 rounded-[28px] border border-black/5 bg-white p-8 shadow-[0_10px_40px_rgba(0,0,0,0.04)] sm:grid-cols-4 sm:p-10"
        >
          {stat.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-[36px] font-extrabold tracking-tight text-neutral-900">
                <NumberTicker value={s.value} />
                {s.value > 0 ? <span className="text-neutral-300">+</span> : null}
              </div>
              <p
                className="mt-1 text-[11px] uppercase tracking-[0.12em] text-neutral-400"
                style={{ fontFamily: MONO }}
              >
                {s.label}
              </p>
            </div>
          ))}
        </motion.section>

        {/* ===== Tool showcases: Generator + Evaluator ===== */}
        <section className="mb-12 grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Viz Generator */}
          <motion.div
            variants={fade}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: "-60px" }}
            className="flex flex-col rounded-[28px] border border-black/5 bg-white p-8 shadow-[0_10px_40px_rgba(0,0,0,0.04)]"
          >
            <Eyebrow icon={Workflow}>Viz Generator</Eyebrow>
            <h3 className="mt-4 text-[22px] font-bold">Describe it, watch it build</h3>
            <p className="mt-2 text-[14px] text-neutral-500">
              Upload a dataset, type what you want in plain English, and the assistant generates the
              right chart instantly.
            </p>
            <div className="mt-6 h-[230px]">
              <GeneratorShowcase accent="#6d5bd0" />
            </div>
            <button
              type="button"
              onClick={() => nav("viz_generator")}
              className="mt-6 inline-flex w-fit items-center gap-2 rounded-xl bg-neutral-900 px-5 py-3 text-[12px] uppercase tracking-[0.12em] text-white transition-colors hover:bg-neutral-800"
              style={{ fontFamily: MONO }}
            >
              Open Generator <ArrowUpRight className="h-4 w-4" />
            </button>
          </motion.div>

          {/* Viz Evaluator */}
          <motion.div
            variants={fade}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: "-60px" }}
            className="flex flex-col rounded-[28px] border border-black/5 bg-white p-8 shadow-[0_10px_40px_rgba(0,0,0,0.04)]"
          >
            <Eyebrow icon={BarChart3}>Viz Evaluator</Eyebrow>
            <h3 className="mt-4 text-[22px] font-bold">Score any chart on quality</h3>
            <p className="mt-2 text-[14px] text-neutral-500">
              Upload a visualization image and the AI reviews labels, color, and clarity — then
              returns an actionable quality score.
            </p>
            <div className="mt-6 h-[230px]">
              <EvaluatorShowcase accent="#5b8c5a" />
            </div>
            <button
              type="button"
              onClick={() => nav("viz_evaluator")}
              className="mt-6 inline-flex w-fit items-center gap-2 rounded-xl border border-neutral-300 bg-white px-5 py-3 text-[12px] uppercase tracking-[0.12em] text-neutral-900 transition-colors hover:bg-neutral-50"
              style={{ fontFamily: MONO }}
            >
              Open Evaluator <ArrowUpRight className="h-4 w-4" />
            </button>
          </motion.div>
        </section>

        {/* ===== Platform breakdown strip ===== */}
        <section className="mb-16 rounded-[28px] border border-black/5 bg-white p-8 shadow-[0_10px_40px_rgba(0,0,0,0.04)]">
          <Eyebrow icon={BarChart3}>Platform breakdown</Eyebrow>
          <h3 className="mt-4 text-[22px] font-bold">Charts produced across the platform</h3>
          {chartTypes.length > 0 ? (
            <div className="mt-6 grid grid-cols-1 gap-x-10 gap-y-4 sm:grid-cols-2">
              {chartTypes.map((item) => (
                <div key={item.viz_type}>
                  <div className="mb-1.5 flex justify-between text-[13px]">
                    <span className="capitalize text-neutral-700">{item.viz_type}</span>
                    <span className="text-neutral-400">{item.count}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-neutral-100">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ background: "linear-gradient(90deg,#6d5bd0,#a78bfa)" }}
                      initial={{ width: 0 }}
                      whileInView={{ width: `${(item.count / maxChart) * 100}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.8 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-6 flex flex-wrap gap-2">
              {(supportedCharts.length ? supportedCharts : ["bar", "line", "scatter", "pie"]).map(
                (chart) => (
                  <span
                    key={chart}
                    className="rounded-full border border-neutral-200 bg-neutral-50 px-3.5 py-1.5 text-[12px] text-neutral-600"
                  >
                    {chart}
                  </span>
                ),
              )}
            </div>
          )}
        </section>

        {/* ===== FAQ ===== */}
        <section id="faq" className="scroll-mt-10 pb-24 pt-4">
          <div className="flex justify-center">
            <Eyebrow>FAQ</Eyebrow>
          </div>
          <h2 className="mt-6 text-center text-[30px] font-bold tracking-tight sm:text-[44px]">
            Frequently asked questions
          </h2>
          <div className="mx-auto mt-12 max-w-[760px] space-y-3">
            {faqs.map((f, i) => {
              const open = openFaq === i;
              return (
                <div key={i} className="overflow-hidden rounded-[18px] border border-black/5 bg-white">
                  <button
                    type="button"
                    onClick={() => setOpenFaq(open ? null : i)}
                    className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                  >
                    <span className="text-[16px] font-semibold">{f.q}</span>
                    {open ? (
                      <Minus className="h-5 w-5 shrink-0 text-neutral-900" />
                    ) : (
                      <Plus className="h-5 w-5 shrink-0 text-neutral-400" />
                    )}
                  </button>
                  {open && <p className="px-6 pb-5 text-[15px] leading-relaxed text-neutral-500">{f.a}</p>}
                </div>
              );
            })}
          </div>
        </section>

        {/* ===== Admin ===== */}
        {isAdmin && (
          <section className="pb-12">
            <div className="flex flex-wrap items-center justify-between gap-4 rounded-[28px] border border-neutral-900 bg-neutral-900 p-8 text-white">
              <div>
                <span
                  className="text-[12px] uppercase tracking-[0.14em] text-violet-300"
                  style={{ fontFamily: MONO }}
                >
                  Admin
                </span>
                <h3 className="mt-1 text-[24px] font-bold">Platform Analytics</h3>
                <p className="mt-1 text-[14px] text-white/60">
                  Track usage, chart trends, and user activity across the platform.
                </p>
              </div>
              <button
                type="button"
                onClick={() => nav("analytics_dashboard")}
                className="rounded-xl bg-white px-6 py-3 text-[13px] uppercase tracking-[0.12em] text-neutral-900 hover:bg-neutral-100"
                style={{ fontFamily: MONO }}
              >
                Open Analytics
              </button>
            </div>
          </section>
        )}

        {/* ===== Footer CTA banner ===== */}
        <section className="pb-16">
          <div className="relative overflow-hidden rounded-[32px] border border-black/5 px-8 py-20 text-center shadow-[0_10px_40px_rgba(0,0,0,0.05)]">
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "linear-gradient(110deg, #efe9fb 0%, #ffffff 38%, #ffffff 62%, #e7f3ec 100%)",
              }}
            />
            <div className="relative">
              <div className="flex justify-center">
                <Eyebrow icon={Sparkles}>Next-Generation AI Platform</Eyebrow>
              </div>
              <h2 className="mx-auto mt-6 max-w-[640px] text-[32px] font-extrabold leading-[1.1] tracking-tight sm:text-[48px]">
                Start Using Your AI Data Assistant Today
              </h2>
              <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
                <PrimaryBtn onClick={() => nav("viz_generator")}>
                  Get Started Free <ArrowUpRight className="h-4 w-4" />
                </PrimaryBtn>
                <GhostBtn onClick={() => nav("viz_evaluator")}>Try Evaluator</GhostBtn>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* ===== Dark footer ===== */}
      <footer className="bg-neutral-950 text-white">
        <div className="mx-auto w-full px-6 py-16 sm:px-10 lg:px-16 xl:px-20">
          <div className="grid grid-cols-1 gap-10 md:grid-cols-12">
            {/* Brand block */}
            <div className="md:col-span-5">
              <button type="button" onClick={() => nav("home")} className="flex items-center gap-2">
                <VisualStatsLogo className="h-8 w-8" />
                <span className="text-[18px] font-bold tracking-tight">VisualStats</span>
              </button>
              <p className="mt-5 max-w-[320px] text-[14px] leading-relaxed text-white/55">
                An AI platform that turns raw datasets into clear visualizations and evaluates chart
                quality — all through conversation.
              </p>
              <div className="mt-6 flex items-center gap-3">
                {socialIcons.map((s) => (
                  <span
                    key={s.label}
                    title={s.label}
                    className="flex h-9 w-9 cursor-default items-center justify-center rounded-full bg-white/10 text-white/70 transition-colors hover:bg-white/20 hover:text-white"
                  >
                    {s.icon}
                  </span>
                ))}
              </div>
            </div>

            {/* Link columns */}
            {footerColumns.map((col) => (
              <div key={col.title} className="md:col-span-2">
                <h4 className="text-[15px] font-semibold text-white">{col.title}</h4>
                <ul className="mt-4 space-y-3">
                  {col.links.map((link) => (
                    <li key={link.label}>
                      <button
                        type="button"
                        onClick={() => handleFooterLink(link.target)}
                        className={`text-[14px] text-white/55 transition-colors hover:text-white ${
                          link.target ? "cursor-pointer" : "cursor-default"
                        }`}
                      >
                        {link.label}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-white/10 pt-8 text-[13px] text-white/45 sm:flex-row">
            <span>© VisualStats {new Date().getFullYear()}. All rights reserved.</span>
            <span style={{ fontFamily: MONO }} className="text-[11px] uppercase tracking-[0.14em]">
              AI-powered data visualization
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};

/* Footer link columns and social icons. */
const footerColumns: {
  title: string;
  links: { label: string; target?: string }[];
}[] = [
  {
    title: "Product",
    links: [
      { label: "Home", target: "home" },
      { label: "Viz Generator", target: "viz_generator" },
      { label: "Viz Evaluator", target: "viz_evaluator" },
      { label: "Logout", target: "logout" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Capabilities", target: "capabilities" },
      { label: "Platform stats" },
    ],
  },
  {
    title: "Legal",
    links: [{ label: "Privacy policy" }, { label: "Terms & conditions" }],
  },
];

const socialIcons: { label: string; icon: React.ReactNode }[] = [
  {
    label: "X",
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.66l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
      </svg>
    ),
  },
  {
    label: "GitHub",
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor">
        <path d="M12 .5C5.73.5.5 5.73.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2c-3.2.7-3.88-1.54-3.88-1.54-.53-1.34-1.3-1.7-1.3-1.7-1.06-.72.08-.71.08-.71 1.17.08 1.78 1.2 1.78 1.2 1.04 1.78 2.73 1.27 3.4.97.1-.75.41-1.27.74-1.56-2.55-.29-5.23-1.28-5.23-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.79 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.69 5.39-5.25 5.68.42.36.79 1.08.79 2.18v3.23c0 .31.21.68.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.73 18.27.5 12 .5z" />
      </svg>
    ),
  },
  {
    label: "LinkedIn",
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor">
        <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.13 1.45-2.13 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45zM5.34 7.43a2.07 2.07 0 1 1 0-4.13 2.07 2.07 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.22.79 24 1.77 24h20.45c.98 0 1.78-.78 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z" />
      </svg>
    ),
  },
];

/** Inline coloured icon chip used inside the capabilities headline. */
function InlineWord({
  color,
  icon: Icon,
  children,
}: {
  color: string;
  icon: React.ComponentType<{ className?: string }>;
  children?: React.ReactNode;
}) {
  return (
    <>
      {children}
      <span
        className="mx-1.5 inline-flex h-9 w-9 translate-y-1.5 items-center justify-center rounded-xl align-middle"
        style={{ background: `${color}22`, color }}
      >
        <Icon className="h-5 w-5" />
      </span>
    </>
  );
}

export default MagicDashboard;
