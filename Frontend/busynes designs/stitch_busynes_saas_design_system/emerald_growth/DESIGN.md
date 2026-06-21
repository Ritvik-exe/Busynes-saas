---
name: Emerald Growth
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#404a3b'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#707a6a'
  outline-variant: '#bfcab7'
  surface-tint: '#066e08'
  primary: '#005f03'
  on-primary: '#ffffff'
  primary-container: '#1b7a16'
  on-primary-container: '#abff97'
  inverse-primary: '#7edc6d'
  secondary: '#515f74'
  on-secondary: '#ffffff'
  secondary-container: '#d5e3fd'
  on-secondary-container: '#57657b'
  tertiary: '#4f5254'
  on-tertiary: '#ffffff'
  tertiary-container: '#676a6c'
  on-tertiary-container: '#e9ebed'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#9af986'
  primary-fixed-dim: '#7edc6d'
  on-primary-fixed: '#002200'
  on-primary-fixed-variant: '#005302'
  secondary-fixed: '#d5e3fd'
  secondary-fixed-dim: '#b9c7e0'
  on-secondary-fixed: '#0d1c2f'
  on-secondary-fixed-variant: '#3a485c'
  tertiary-fixed: '#e0e3e5'
  tertiary-fixed-dim: '#c4c7c9'
  on-tertiary-fixed: '#191c1e'
  on-tertiary-fixed-variant: '#444749'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
---

## Brand & Style

This design system is built for growth-oriented financial services and corporate technology. The brand personality is authoritative yet vibrant, signaling both stability and prosperity. It leverages a **Corporate / Modern** aesthetic with high-precision alignment and intentional whitespace.

The visual narrative focuses on "Growth" through the use of a deep emerald green, balanced by "Professional Slate" to ground the interface in reliability. The design should evoke a sense of clarity, efficiency, and momentum. It avoids unnecessary decoration, favoring functional elegance and crisp typographic hierarchy to guide users through complex data and workflows.

## Colors

The palette is anchored by a specific **Emerald Green (#1B7A16)** extracted from the brand identity, symbolizing growth and financial vitality. This is the primary action color.

- **Primary (Emerald):** Used for primary buttons, active states, progress indicators, and key data highlights.
- **Secondary (Professional Slate):** A deep, cool slate used for headings, primary navigation elements, and high-contrast text to ensure a professional foundation.
- **Surface (Crisp White):** The primary background color (#FFFFFF), maintaining a clean, editorial feel.
- **Neutral:** A range of grays used for borders, secondary text, and disabled states to provide subtle scaffolding without competing with the primary green.

## Typography

The typography system uses a tri-font approach to balance modernity, readability, and technical precision.

- **Hanken Grotesk** is used for headlines. Its contemporary geometry feels fresh and professional. Use tighter letter-spacing for larger displays to maintain visual impact.
- **Inter** handles all body copy and UI text. It is chosen for its exceptional legibility at small sizes and its neutral, systematic tone.
- **JetBrains Mono** is utilized for labels, captions, and data-specific strings (like currency or account numbers) to provide a technical, high-precision edge to the financial context.

## Layout & Spacing

The design system utilizes a **12-column fluid grid** for desktop and a **4-column grid** for mobile. The rhythm is based on an 8px square baseline grid, ensuring all components and containers align perfectly.

- **Desktop:** 12 columns, 24px gutters, 64px side margins. Max-width of 1440px for content containers.
- **Tablet:** 8 columns, 24px gutters, 32px side margins.
- **Mobile:** 4 columns, 16px gutters, 16px side margins.

Horizontal spacing should follow the defined increments to create a clear visual hierarchy. Large "xl" spacing is encouraged between major sections to emphasize the "Minimalist" influence and allow the Emerald accents to breathe.

## Elevation & Depth

This design system uses **Tonal Layers** and **Low-contrast outlines** rather than heavy shadows to maintain a "Crisp" feel.

- **Level 0 (Base):** Crisp White (#FFFFFF).
- **Level 1 (Cards/Surface):** Primary background with a 1px border (#E2E8F0).
- **Level 2 (Navigation/Overlays):** Uses a very soft, highly diffused ambient shadow (0px 4px 20px rgba(0, 0, 0, 0.05)) to suggest a slight lift without appearing heavy.
- **Interactive States:** On hover, primary buttons should darken slightly, and cards should transition to a Level 2 elevation with a subtle Emerald-tinted border (#1B7A16 at 20% opacity).

## Shapes

The shape language is **Soft (0.25rem)**. This slight rounding takes the edge off the professional slate colors without moving into "playful" territory. It reflects the precision of a corporate tool while remaining approachable.

- **Small Components:** Checkboxes and small buttons use the 0.25rem (4px) base.
- **Containers:** Large cards and modals use `rounded-lg` (0.5rem / 8px) to establish a clear boundary.
- **Selection States:** Pill shapes (full rounding) are reserved exclusively for "Status Tags" or "Chips" to differentiate them from interactive buttons.

## Components

### Buttons
- **Primary:** Background of #1B7A16 (Emerald) with white text. High-contrast, 4px corner radius.
- **Secondary:** Transparent background with #1B7A16 border and text.
- **Ghost:** No border, Professional Slate text, subtle gray background on hover.

### Input Fields
Inputs should use a 1px border (#E2E8F0). Focus states are signaled by a 2px Emerald border and a very light green glow. Labels use **Inter** Semibold at 14px.

### Chips & Tags
Used for status (e.g., "Active", "Pending"). These are pill-shaped. "Active" states must use a light Emerald tint background with dark Emerald text.

### Cards
Cards are the primary container for data. They feature 1px Professional Slate-tinted borders and no shadow by default, creating a flat, organized "dashboard" look.

### Lists
List items should have generous vertical padding (16px) and subtle dividers (#F1F5F9). Icons within lists should use the Professional Slate color unless they represent a positive growth metric, in which case Emerald Green is used.