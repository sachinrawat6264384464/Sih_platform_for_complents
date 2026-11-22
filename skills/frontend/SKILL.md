---
name: aicte-nexus-frontend
description: Frontend design system, themes, water ripple effects, animated clouds, and component architecture for AICTE Nexus
---

# Frontend Skill - AICTE Nexus

## Design System & Government Aesthetics
- **Theme 1: Dark (Executive Command)**:
  - Primary Background: `#0B1730`
  - Secondary / Card: `#14233D`
  - Primary Accent / Orange: `#F28C28`
  - Secondary Accent: `#FF9F43`
  - Typography: Primary `#F4F7FC`, Muted `#A8BAD1`
- **Theme 2: Light (National Portal)**:
  - Primary Background: `#F1F8FF`
  - Surface / Cards: `#FFFFFF`
  - Sky Blue Accent: `#1686CB` / `#6CBCEB`
  - Text: Navy `#10243E`
  - Borders: `#D8E8F6`

## Special Visual Effects
1. **Interactive Water Ripple Cursor**:
   - Small liquid ripple following the pointer using Canvas or SVG throttled via `requestAnimationFrame`.
   - Disabled on touch screens and when `prefers-reduced-motion` is active.
   - Pointer events pass through completely to prevent blocking clicks, selection, or input.
2. **Subtle Animated Cloud Background**:
   - Soft, slow-moving atmospheric clouds representing national reach.
   - Toggleable from the UI header settings.
3. **Ambient Rain Effect**:
   - Optional subtle monsoon rain overlay toggleable from the theme settings.
4. **Command Palette (`Ctrl+K` / `Cmd+K`)**:
   - Instant keyboard-driven global navigation across institutions, complaints, cases, and settings.

