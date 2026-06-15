---
name: VisualStats
description: Automatic Generation of Visualizations and Infographics with LLMs
colors:
  primary: "#0066CC"
  primary-dark: "#0052A3"
  secondary: "#10B981"
  danger: "#EF4444"
  warning: "#F59E0B"
  light: "#F8FAFC"
  border: "#E2E8F0"
  text: "#1E293B"
  text-secondary: "#64748B"
typography:
  display:
    fontFamily: "system-ui, -apple-system, sans-serif"
    fontWeight: 800
  headline:
    fontFamily: "system-ui, -apple-system, sans-serif"
    fontWeight: 700
  body:
    fontFamily: "system-ui, -apple-system, sans-serif"
    fontWeight: 400
rounded:
  sm: "8px"
  md: "10px"
  lg: "12px"
spacing:
  sm: "15px"
  md: "20px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.sm}"
  card:
    backgroundColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
---

# Design System: VisualStats

## 1. Overview

**Creative North Star: "The Data Studio"**

This system is modern, breezy, and approachable. It strikes a perfect balance between professionalism and ease-of-use, transforming complex data tasks into a clean, intuitive experience. The aesthetic philosophy prioritizes clarity over density, ensuring that the generated visualization is always the central focus without overwhelming the user with unnecessary visual clutter.

We explicitly reject overly crowded or dense dashboards and interfaces that dump too much information on the screen at once (as seen in traditional enterprise BI tools).

**Key Characteristics:**
- **Approachable Professionalism:** A clean, airy layout that doesn't intimidate.
- **Clear Hierarchy:** Content is lifted into distinct cards to guide the eye.
- **Tactile Responses:** Interactive elements respond clearly to user action.

## 2. Colors

A balanced palette anchored by a strong primary blue and supportive greens, set against a crisp, light background.

### Primary
- **Insight Blue** (#0066CC): The core brand color, used for primary actions, active tabs, and critical UI accents.
- **Insight Blue Deep** (#0052A3): Used for hover states and gradient pairings to add depth.

### Secondary
- **Growth Green** (#10B981): Used for success states, confirmations, and positive trend indicators.

### Neutral
- **Slate Text** (#1E293B): Primary text color for high legibility.
- **Muted Slate** (#64748B): Secondary text color for helper text and inactive tabs.
- **Breezy Background** (#F8FAFC): The main app background, providing an airy, modern feel.
- **Soft Border** (#E2E8F0): Used to delineate cards and inputs without heavy lines.

### Named Rules
**The Background Canvas Rule.** The main app background is always Breezy Background (#F8FAFC), allowing stark white cards to pop forward.

## 3. Typography

**Display Font:** System Sans (e.g., San Francisco, Inter, or Roboto)
**Body Font:** System Sans

**Character:** Clean, highly legible, and unornamented. It supports the data without drawing attention to itself.

### Hierarchy
- **Display** (800 weight, large): Hero banners and major page titles.
- **Headline** (700 weight): Section headers and card titles.
- **Body** (400 weight): Standard paragraph text and chat responses.

### Named Rules
**The Legibility Rule.** Never use weights below 400 for structural text, ensuring crisp rendering across devices.

## 4. Elevation

The system uses a "Lifted" philosophy. Surfaces float above the breezy background to establish clear structural hierarchy. Depth is created through soft, diffuse shadows.

### Shadow Vocabulary
- **Card Lift** (`box-shadow: 0 2px 8px rgba(0,0,0,0.08)`): The standard resting elevation for all cards and containers.
- **Hover Lift** (`box-shadow: 0 8px 20px rgba(0, 102, 204, 0.3)`): Used on primary buttons to provide a tactile "pressable" feel.

### Named Rules
**The Hover Feedback Rule.** Interactive elements must provide clear visual feedback. Buttons should lift and intensify in color when hovered.

## 5. Components

Tactile and responsive with clear hover states, ensuring users always know what is clickable.

### Buttons
- **Shape:** Rounded (8px radius)
- **Primary:** Insight Blue to Insight Blue Deep linear-gradient, white text.
- **Hover / Focus:** Lifts up (`translateY(-2px)`) with a strong colored shadow (`rgba(0, 102, 204, 0.3)`).

### Cards / Containers
- **Corner Style:** Rounded (10px radius)
- **Background:** White
- **Shadow Strategy:** Card Lift (diffuse 8% opacity shadow).
- **Border:** 1px solid Soft Border (#E2E8F0)
- **Internal Padding:** 20px standard padding.

### Inputs / Fields
- **Style:** 8px radius, clean borders. File uploaders use a 2px dashed Insight Blue border.
- **Focus:** Highlighted borders to indicate active typing.

### Navigation
- **Style, typography, default/hover/active states, mobile treatment:** Bottom-bordered tabs. Inactive text is Muted Slate. Active tabs are Insight Blue with a 3px bottom border.

## 6. Do's and Don'ts

Concrete guardrails to maintain the "Data Studio" aesthetic.

### Do:
- **Do** rely on the chat interface as the primary driver of changes.
- **Do** ensure the generated visualization remains the hero of the screen.
- **Do** use `box-shadow: 0 2px 8px rgba(0,0,0,0.08)` to lift white cards off the `#F8FAFC` background.
- **Do** provide tactile hover states (`translateY(-2px)`) on all primary buttons.

### Don't:
- **Don't** create overly crowded or dense dashboards (e.g., traditional enterprise BI tools).
- **Don't** dump too much information on the screen at once.
- **Don't** use dark mode or neon accents that conflict with the breezy, approachable feel.
