import React, { useState, useRef, useCallback } from "react";
import { Streamlit } from "streamlit-component-lib";
import { motion, AnimatePresence } from "framer-motion";

// ——— Interactive Right Panel ———
function VisualizationPanel() {
  const panelRef = useRef<HTMLDivElement>(null);
  const [mouse, setMouse] = useState({ x: 0.5, y: 0.5 });
  const [isHovering, setIsHovering] = useState(false);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!panelRef.current) return;
    const rect = panelRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
    setMouse({ x, y });
    setIsHovering(true);
  }, []);

  // Generate smooth curve data
  const dataPoints = React.useMemo(() => {
    const pts = [];
    for (let i = 0; i <= 20; i++) {
      pts.push({
        x: i * 5, // 0 to 100%
        y1: 30 + Math.sin(i * 0.4) * 20 + Math.cos(i * 0.7) * 10,
        y2: 60 + Math.cos(i * 0.3) * 15 + Math.sin(i * 0.8) * 10,
      });
    }
    return pts;
  }, []);

  const buildPath = (key: 'y1' | 'y2') => {
    return dataPoints.reduce((acc, pt, i) => {
      if (i === 0) return `M ${pt.x} ${pt[key]}`;
      const prev = dataPoints[i - 1];
      const cx1 = prev.x + (pt.x - prev.x) / 2;
      const cy1 = prev[key];
      const cx2 = prev.x + (pt.x - prev.x) / 2;
      const cy2 = pt[key];
      return `${acc} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${pt.x} ${pt[key]}`;
    }, "");
  };

  const path1 = buildPath('y1');
  const path2 = buildPath('y2');

  // Interpolate data for tooltip
  const hoverXIndex = Math.min(Math.max(Math.round(mouse.x * 20), 0), 20);
  const currentData = dataPoints[hoverXIndex];

  return (
    <div
      ref={panelRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setIsHovering(false)}
      style={{
        flex: 1,
        position: "relative",
        overflow: "hidden",
        borderRadius: 16,
        margin: 16,
        background: "#08090f",
        padding: "2rem",
        minHeight: 400,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "inset 0 0 100px rgba(0,0,0,0.5)",
      }}
    >
      {/* Background Masked Grid - Flashlight effect */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundSize: "30px 30px",
          backgroundImage: "radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px)",
          zIndex: 0,
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundSize: "30px 30px",
          backgroundImage: "radial-gradient(rgba(99,102,241,0.4) 1.5px, transparent 1.5px)",
          WebkitMaskImage: `radial-gradient(300px circle at ${mouse.x * 100}% ${mouse.y * 100}%, black, transparent)`,
          maskImage: `radial-gradient(300px circle at ${mouse.x * 100}% ${mouse.y * 100}%, black, transparent)`,
          zIndex: 1,
          pointerEvents: "none",
          transition: "mask-image 0.1s ease-out, -webkit-mask-image 0.1s ease-out",
        }}
      />

      {/* Floating Prompt Bubble */}
      <motion.div
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        style={{
          position: "absolute",
          top: "10%",
          left: "10%",
          background: "rgba(30, 41, 59, 0.7)",
          backdropFilter: "blur(12px)",
          border: "1px solid rgba(148, 163, 184, 0.2)",
          padding: "12px 20px",
          borderRadius: "20px 20px 20px 4px",
          zIndex: 10,
          boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
          maxWidth: 250,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#6366f1" }} />
          <span style={{ fontSize: 11, fontWeight: 600, color: "#94a3b8" }}>USER QUERY</span>
        </div>
        <p style={{ margin: 0, fontSize: 13, color: "#e2e8f0", lineHeight: 1.4 }}>
          "Visualize the correlation between inference latency and model accuracy across batches..."
        </p>
      </motion.div>

      {/* Interactive Main Chart Dashboard */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        style={{
          width: "100%",
          maxWidth: 600,
          height: 350,
          background: "linear-gradient(180deg, rgba(15,23,42,0.8) 0%, rgba(15,23,42,0.4) 100%)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(99,102,241,0.2)",
          borderRadius: 16,
          padding: "24px",
          position: "relative",
          zIndex: 5,
          boxShadow: "0 20px 50px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1)",
          display: "flex",
          flexDirection: "column",
          transform: `perspective(1000px) rotateX(${(0.5 - mouse.y) * 10}deg) rotateY(${(mouse.x - 0.5) * 10}deg)`,
          transformStyle: "preserve-3d",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <div>
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: "#f8fafc" }}>Inference Performance</h3>
            <p style={{ margin: 0, fontSize: 12, color: "#64748b", marginTop: 2 }}>Real-time LIDA Visualization generated</p>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ef4444" }} />
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#f59e0b" }} />
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#10b981" }} />
          </div>
        </div>

        {/* The SVG Chart */}
        <div style={{ flex: 1, position: "relative", minHeight: 0 }}>
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", overflow: "hidden" }}>
            <defs>
              <linearGradient id="grad1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
              </linearGradient>
              <linearGradient id="grad2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
              </linearGradient>
            </defs>

            {/* Grid lines */}
            {[20, 40, 60, 80].map(y => (
              <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />
            ))}

            {/* Area 1 */}
            <motion.path
              d={`${path1} L 100 100 L 0 100 Z`}
              fill="url(#grad1)"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 1 }}
            />
            <motion.path
              d={path1}
              fill="none"
              stroke="#818cf8"
              strokeWidth="1.5"
              strokeLinecap="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 0.5, duration: 1.5, ease: "easeOut" }}
            />

            {/* Area 2 */}
            <motion.path
              d={`${path2} L 100 100 L 0 100 Z`}
              fill="url(#grad2)"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7, duration: 1 }}
            />
            <motion.path
              d={path2}
              fill="none"
              stroke="#34d399"
              strokeWidth="1.5"
              strokeLinecap="round"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ delay: 0.7, duration: 1.5, ease: "easeOut" }}
            />

            {/* Interactive Vertical Hover Line */}
            <AnimatePresence>
              {isHovering && (
                <motion.line
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  x1={currentData.x}
                  y1="0"
                  x2={currentData.x}
                  y2="100"
                  stroke="rgba(255,255,255,0.3)"
                  strokeWidth="0.5"
                  strokeDasharray="2,2"
                />
              )}
            </AnimatePresence>

            {/* Hover Dots */}
            <AnimatePresence>
              {isHovering && (
                <>
                  <motion.circle
                    cx={currentData.x}
                    cy={currentData.y1}
                    r="1.5"
                    fill="#818cf8"
                    stroke="#fff"
                    strokeWidth="0.5"
                  />
                  <motion.circle
                    cx={currentData.x}
                    cy={currentData.y2}
                    r="1.5"
                    fill="#34d399"
                    stroke="#fff"
                    strokeWidth="0.5"
                  />
                </>
              )}
            </AnimatePresence>
          </svg>

          {/* Floating Tooltip HTML Overlay */}
          <AnimatePresence>
            {isHovering && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                style={{
                  position: "absolute",
                  left: `${currentData.x}%`,
                  top: "10%",
                  transform: "translateX(-50%)",
                  background: "rgba(0,0,0,0.8)",
                  backdropFilter: "blur(4px)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  padding: "8px 12px",
                  borderRadius: 8,
                  pointerEvents: "none",
                  minWidth: 100,
                  zIndex: 20,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
                }}
              >
                <div style={{ fontSize: 10, color: "#94a3b8", marginBottom: 4 }}>
                  Batch {Math.round(currentData.x)}
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#818cf8" }} />
                    <span style={{ fontSize: 11, color: "#f8fafc" }}>Latency</span>
                  </div>
                  <span style={{ fontSize: 11, fontWeight: 600, color: "#f8fafc", fontFamily: "monospace" }}>
                    {Math.round(100 - currentData.y1)}ms
                  </span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399" }} />
                    <span style={{ fontSize: 11, color: "#f8fafc" }}>Accuracy</span>
                  </div>
                  <span style={{ fontSize: 11, fontWeight: 600, color: "#f8fafc", fontFamily: "monospace" }}>
                    {(100 - currentData.y2).toFixed(1)}%
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Floating Insight Card */}
      <motion.div
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
        style={{
          position: "absolute",
          bottom: "10%",
          right: "10%",
          background: "rgba(16, 185, 129, 0.1)",
          backdropFilter: "blur(12px)",
          border: "1px solid rgba(16, 185, 129, 0.3)",
          padding: "12px 16px",
          borderRadius: "8px",
          zIndex: 10,
          boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <div style={{ background: "rgba(16, 185, 129, 0.2)", padding: 8, borderRadius: 6 }}>
          <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#34d399" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div>
          <div style={{ fontSize: 11, fontWeight: 600, color: "#34d399" }}>INSIGHT DETECTED</div>
          <div style={{ fontSize: 12, color: "#e2e8f0", marginTop: 2 }}>Optimal batch size identified</div>
        </div>
      </motion.div>

      {/* Code Stream Animation (Background) */}
      <div
        style={{
          position: "absolute",
          top: "40%",
          right: "0%",
          transform: "rotate(15deg)",
          opacity: 0.2,
          zIndex: 1,
          pointerEvents: "none",
          fontFamily: "'SF Mono', 'Fira Code', monospace",
          fontSize: 12,
          color: "#818cf8",
          lineHeight: 1.8,
          whiteSpace: "pre",
        }}
      >
        <motion.div
          animate={{ y: [0, -100] }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        >
          {`def generate_chart(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=data, x='batch', y='latency', ax=ax)
    sns.lineplot(data=data, x='batch', y='accuracy', ax=ax)
    ax.set_title('Model Performance Metrics')
    ax.grid(True, alpha=0.3)
    return fig

# Executing LIDA visualization pipeline...
summary = lida.summarize(dataset)
goals = lida.goals(summary, n=3)
charts = lida.visualize(summary=summary, goal=goals[0])`}
        </motion.div>
      </div>
    </div>
  );
}

// ——————————————————————————————
// Main MagicAuth Component
// ——————————————————————————————
export default function MagicAuth({ errorMessage }: { errorMessage?: string }) {
  const [isAdmin, setIsAdmin] = useState(false);
  const [username, setUsername] = useState("");
  const [pin, setPin] = useState("");
  const [masterCode, setMasterCode] = useState("");

  const handleSubmit = (
    e: React.FormEvent<HTMLFormElement> | React.MouseEvent<HTMLButtonElement>,
    action: "login" | "guest" | "register"
  ) => {
    e.preventDefault();
    Streamlit.setComponentValue({
      action,
      username,
      pin,
      master_code: masterCode,
      is_admin: isAdmin,
      timestamp: Date.now(),
    });
  };

  // ——— Styles ———
  const pageStyle: React.CSSProperties = {
    display: "flex",
    minHeight: "100vh",
    width: "100%",
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    background: "#0a0a0a",
    color: "#fafafa",
  };

  const leftCol: React.CSSProperties = {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    padding: "3rem 4rem",
    maxWidth: 520,
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    height: 44,
    background: "#171717",
    border: "1px solid #2a2a2a",
    borderRadius: 8,
    padding: "0 14px",
    color: "#fafafa",
    fontSize: 14,
    outline: "none",
    boxSizing: "border-box",
    marginTop: 8,
    transition: "border-color 0.2s ease",
  };

  const labelStyle: React.CSSProperties = {
    fontSize: 14,
    fontWeight: 500,
    color: "#a1a1aa",
    marginBottom: 4,
  };

  const primaryBtn: React.CSSProperties = {
    width: "100%",
    height: 44,
    background: "#fafafa",
    color: "#0a0a0a",
    border: "none",
    borderRadius: 10,
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    transition: "all 0.15s ease",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  };

  const secondaryBtn: React.CSSProperties = {
    width: "100%",
    height: 44,
    background: "transparent",
    color: "#a1a1aa",
    border: "1px solid #2a2a2a",
    borderRadius: 10,
    fontSize: 14,
    fontWeight: 500,
    cursor: "pointer",
    transition: "all 0.15s ease",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  };

  const dividerStyle: React.CSSProperties = {
    display: "flex",
    alignItems: "center",
    gap: 16,
    margin: "28px 0",
  };

  const dividerLine: React.CSSProperties = {
    flex: 1,
    height: 1,
    background: "#2a2a2a",
  };

  return (
    <div style={pageStyle}>
      {/* ——— Left Column: Form ——— */}
      <motion.div
        style={leftCol}
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        {/* Logo */}
        <svg
          width="28"
          height="28"
          viewBox="0 0 20 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{ marginBottom: 24 }}
        >
          <path
            d="M0 4.5C0 3.119 1.119 2 2.5 2H7.5C8.881 2 10 3.119 10 4.5V9.41C10 10.879 11.116 12 12.494 12H17.5C18.881 12 20 13.119 20 14.5V19.5C20 20.881 18.881 22 17.5 22H12.5C11.119 22 10 20.881 10 19.5V14.5C10 13.108 8.874 12 7.5 12H2.5C1.119 12 0 10.881 0 9.5V4.5Z"
            fill="#fafafa"
          />
        </svg>

        <h1
          style={{
            fontSize: 32,
            fontWeight: 600,
            letterSpacing: "-0.025em",
            margin: 0,
            color: "#fafafa",
          }}
        >
          Welcome to VisualStats
        </h1>
        <p
          style={{
            fontSize: 14,
            color: "#71717a",
            marginTop: 8,
            marginBottom: 32,
            lineHeight: 1.6,
          }}
        >
          {isAdmin
            ? "Admin access portal — enter your credentials and master code."
            : "Sign in or register instantly with your username and PIN."}
        </p>

        <form
          onSubmit={(e) => handleSubmit(e, "login")}
          style={{ display: "flex", flexDirection: "column", gap: 20 }}
        >
          <div>
            <label style={labelStyle}>Username</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={inputStyle}
              onFocus={(e) => (e.target.style.borderColor = "#525252")}
              onBlur={(e) => (e.target.style.borderColor = "#2a2a2a")}
            />
          </div>

          <div>
            <label style={labelStyle}>4-Digit PIN</label>
            <input
              type="password"
              placeholder="••••"
              maxLength={4}
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              style={{
                ...inputStyle,
                letterSpacing: "0.3em",
                fontFamily: "monospace",
              }}
              onFocus={(e) => (e.target.style.borderColor = "#525252")}
              onBlur={(e) => (e.target.style.borderColor = "#2a2a2a")}
            />
          </div>

          {isAdmin && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              style={{ overflow: "hidden" }}
            >
              <label style={labelStyle}>Admin Master Code</label>
              <input
                type="password"
                placeholder="Enter 6-digit master code"
                value={masterCode}
                onChange={(e) => setMasterCode(e.target.value)}
                style={inputStyle}
                onFocus={(e) => (e.target.style.borderColor = "#525252")}
                onBlur={(e) => (e.target.style.borderColor = "#2a2a2a")}
              />
            </motion.div>
          )}

          <button
            type="submit"
            style={primaryBtn}
            onMouseEnter={(e) => {
              (e.target as HTMLButtonElement).style.transform = "scale(0.98)";
              (e.target as HTMLButtonElement).style.background = "#e4e4e7";
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLButtonElement).style.transform = "scale(1)";
              (e.target as HTMLButtonElement).style.background = "#fafafa";
            }}
          >
            {isAdmin ? "Login as Admin" : "Sign in"}
            <svg
              width="16" height="16" fill="none" viewBox="0 0 24 24"
              stroke="currentColor" strokeWidth="2"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>

          {isAdmin && (
            <button
              type="button"
              style={secondaryBtn}
              onClick={(e) => handleSubmit(e, "register")}
              onMouseEnter={(e) => {
                (e.target as HTMLButtonElement).style.borderColor = "#525252";
                (e.target as HTMLButtonElement).style.color = "#fafafa";
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLButtonElement).style.borderColor = "#2a2a2a";
                (e.target as HTMLButtonElement).style.color = "#a1a1aa";
              }}
            >
              Register New Admin
            </button>
          )}

          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid rgba(239, 68, 68, 0.3)",
                color: "#fca5a5",
                padding: "12px 16px",
                borderRadius: 8,
                fontSize: 13,
                textAlign: "center",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                marginTop: 4,
              }}
            >
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {errorMessage}
            </motion.div>
          )}
        </form>

        <div style={dividerStyle}>
          <div style={dividerLine} />
          <span style={{ fontSize: 13, color: "#52525b" }}>or</span>
          <div style={dividerLine} />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {!isAdmin && (
            <button
              style={secondaryBtn}
              onClick={(e) => handleSubmit(e, "guest")}
              onMouseEnter={(e) => {
                (e.target as HTMLButtonElement).style.borderColor = "#525252";
                (e.target as HTMLButtonElement).style.color = "#fafafa";
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLButtonElement).style.borderColor = "#2a2a2a";
                (e.target as HTMLButtonElement).style.color = "#a1a1aa";
              }}
            >
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Continue as Guest
            </button>
          )}

          <button
            style={{
              ...secondaryBtn,
              border: "none",
              fontSize: 13,
              height: 36,
              color: "#71717a",
            }}
            onClick={() => {
              setIsAdmin(!isAdmin);
              setMasterCode("");
            }}
            onMouseEnter={(e) => {
              (e.target as HTMLButtonElement).style.color = "#fafafa";
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLButtonElement).style.color = "#71717a";
            }}
          >
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            {isAdmin ? "Switch to User Portal" : "Switch to Admin Portal"}
          </button>
        </div>
      </motion.div>

      {/* ——— Right Column: Interactive Visualizations ——— */}
      <VisualizationPanel />
    </div>
  );
}
