import React, { useEffect, useState, useRef, useLayoutEffect } from 'react'
import { Streamlit } from 'streamlit-component-lib'

import MagicHero from './components/MagicHero'
import MagicDashboard from './components/MagicDashboard'
import MagicFeedback from './components/MagicFeedback'
import MagicAuth from './components/MagicAuth'
import MagicWorkspaceHeader from './components/MagicWorkspaceHeader'
import MagicEmptyCanvas from './components/MagicEmptyCanvas'
import MagicEvaluator from './components/MagicEvaluator'
import MagicAnalytics from './components/MagicAnalytics'
import MagicPageNav from './components/MagicPageNav'

const LIGHT_BG = '#fbfbfa'
const DARK_BG = '#0a0a0a'
const DASH_BG = '#fbfbfa'

class ErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean, error: any}> {
  constructor(props: any) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error: any) { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20, background: '#fee2e2', color: '#991b1b' }}>
          <h2>Component error</h2>
          <pre>{this.state.error?.toString()}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

const App: React.FC = () => {
  const [args, setArgs] = useState<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const lastHeightRef = useRef(0);

  const reportHeight = () => {
    const el = containerRef.current;
    if (!el) return;

    const type = args?.componentType;
    if (type === 'auth') {
      const h = window.innerHeight;
      if (h !== lastHeightRef.current) {
        lastHeightRef.current = h;
        Streamlit.setFrameHeight(h);
      }
      return;
    }

    // Measure only the content wrapper — never document/body scrollHeight,
    // which includes the iframe viewport and causes runaway downward growth.
    const height = Math.ceil(el.offsetHeight);
    if (height <= 20) return;

    if (height !== lastHeightRef.current) {
      lastHeightRef.current = height;
      Streamlit.setFrameHeight(height);
    }
  };

  useEffect(() => {
    const onRender = (event: MessageEvent) => {
      if (event.data.type !== 'streamlit:render') return;
      const newArgs = event.data.args;
      setArgs(newArgs);
      lastHeightRef.current = 0;
      const ct = newArgs?.componentType;
      document.body.style.background = ct === 'auth' ? DARK_BG : ct === 'dashboard' ? DASH_BG : LIGHT_BG;
      document.body.style.margin = '0';
    };
    window.addEventListener('message', onRender);
    Streamlit.setComponentReady();
    Streamlit.setFrameHeight(10);
    return () => window.removeEventListener('message', onRender);
  }, []);

  useLayoutEffect(() => {
    if (!args) return;
    reportHeight();
    const delays = args.componentType === 'dashboard' ? [120, 400, 800, 1500] : [120, 500];
    const timers = delays.map((ms) => window.setTimeout(reportHeight, ms));

    window.addEventListener('resize', reportHeight);

    return () => {
      timers.forEach((t) => clearTimeout(t));
      window.removeEventListener('resize', reportHeight);
    };
  }, [args]);

  let content: React.ReactNode = <div style={{ height: 10 }} />;

  if (args) {
    const { componentType, ...rest } = args;
    switch (componentType) {
      case 'hero':
        content = <MagicHero title={rest.title} subtitle={rest.subtitle} />;
        break;
      case 'dashboard':
        content = (
          <MagicDashboard
            isAdmin={rest.is_admin}
            username={rest.username}
            datasets={rest.datasets || []}
            sessions={rest.sessions || []}
            visualizations={rest.visualizations || []}
            stats={rest.stats}
            chartTypes={rest.chart_types || []}
            supportedCharts={rest.supported_charts || []}
          />
        );
        break;
      case 'workspace':
        content = <MagicWorkspaceHeader title={rest.title} subtitle={rest.subtitle} />;
        break;
      case 'empty_canvas':
        content = <MagicEmptyCanvas title={rest.title} description={rest.description} />;
        break;
      case 'evaluator':
        content = <MagicEvaluator title={rest.title} subtitle={rest.subtitle} />;
        break;
      case 'analytics':
        content = (
          <MagicAnalytics
            totalUsers={rest.total_users}
            totalVisualizations={rest.total_visualizations}
            totalDatasets={rest.total_datasets}
            totalInteractions={rest.total_interactions}
            avgSessionDuration={rest.avg_session_duration}
            topChartTypes={rest.top_chart_types || []}
            topActions={rest.top_actions || []}
          />
        );
        break;
      case 'page_nav':
        content = <MagicPageNav active={rest.active} isAdmin={rest.is_admin} />;
        break;
      case 'feedback':
        content = <MagicFeedback feedback={rest.feedback_text} />;
        break;
      case 'auth':
        content = <MagicAuth errorMessage={rest.error_message} />;
        break;
      default:
        content = <div style={{ color: '#dc2626', padding: 16 }}>Unknown: {componentType}</div>;
    }
  }

  const ct = args?.componentType;
  const isAuth = ct === 'auth';
  const bg = isAuth ? DARK_BG : ct === 'dashboard' ? DASH_BG : LIGHT_BG;

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        overflow: 'hidden',
        background: bg,
        minHeight: isAuth ? '100vh' : undefined,
      }}
    >
      <ErrorBoundary>{content}</ErrorBoundary>
    </div>
  );
};

export default App;
