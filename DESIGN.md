---
name: VisualStats
description: Light vibrant data visualization platform for education
colors:
  primary: "#1E40AF"
  primary-light: "#3B82F6"
  secondary: "#6366F1"
  cta: "#F59E0B"
  success: "#10B981"
  background: "#F8FAFC"
  surface: "#FFFFFF"
  border: "#E2E8F0"
  text: "#1E3A8A"
  text-body: "#334155"
  text-muted: "#64748B"
typography:
  sans: "Fira Sans, ui-sans-serif, system-ui, sans-serif"
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
---

# Design System: VisualStats

## North Star: Vibrant Data Studio

Light, approachable, and visually engaging. Students upload data, converse with AI, and see charts as the hero. Vibrant blue and amber accents on a breezy `#F8FAFC` canvas.

## Colors

- **Primary Blue** `#1E40AF` — actions, nav active, headings
- **Light Blue** `#3B82F6` — gradients, links, chart accents
- **Violet Bridge** `#6366F1` — connects dark auth to light app
- **Amber CTA** `#F59E0B` — primary buttons, highlights
- **Background** `#F8FAFC` — app canvas
- **Surface** `#FFFFFF` — cards, panels

## Typography

Single sans family: **Fira Sans**. Fixed rem scale for product UI (h1 1.75rem, h2 1.5rem, body 1rem).

## Components

- Cards: white surface, 12px radius, subtle shadow, 1px border
- Buttons: blue gradient primary, amber for key CTAs
- No gradient text, no side-stripe borders, no fake hero metrics

## Do

- Chat-first Viz Generator layout
- Real data in dashboard stats
- Lucide icons (not emoji as icons)
- `prefers-reduced-motion` on all animations

## Don't

- Marketing landing patterns on dashboard
- Three competing color systems
- Dense BI-dashboard clutter
