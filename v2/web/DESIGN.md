# ACQUISITOR Design System

## Overview
A premium dark-mode SaaS landing page for ACQUISITOR — an AI-powered business acquisition platform.

## Brand Identity

### Name
ACQUISITOR — Bold, professional, action-oriented

### Personality
- **Confident**: We know what we're doing
- **Premium**: $10M startup aesthetic
- **Trustworthy**: Serious about business acquisition
- **Modern**: AI-first, tech-forward

## Color Palette

### Primary Colors
| Name | Value | Usage |
|------|-------|-------|
| `--bg-primary` | `#030712` (gray-950) | Main background |
| `--bg-secondary` | `#0f172a` (slate-900) | Cards, sections |
| `--bg-tertiary` | `#1e293b` (slate-800) | Elevated surfaces |

### Accent Colors
| Name | Value | Usage |
|------|-------|-------|
| `--accent-indigo` | `#6366f1` (indigo-500) | Primary accent |
| `--accent-purple` | `#8b5cf6` (violet-500) | Secondary accent |
| `--accent-pink` | `#ec4899` (pink-500) | Tertiary accent |
| `--gradient-start` | `#6366f1` | Gradient start |
| `--gradient-mid` | `#8b5cf6` | Gradient middle |
| `--gradient-end` | `#ec4899` | Gradient end |

### Text Colors
| Name | Value | Usage |
|------|-------|-------|
| `--text-primary` | `#ffffff` | Headlines |
| `--text-secondary` | `#94a3b8` (slate-400) | Body text |
| `--text-tertiary` | `#64748b` (slate-500) | Muted text |
| `--text-accent` | `#818cf8` (indigo-400) | Highlighted text |

### Semantic Colors
| Name | Value | Usage |
|------|-------|-------|
| `--success` | `#10b981` (emerald-500) | Success states |
| `--warning` | `#f59e0b` (amber-500) | Warnings |
| `--error` | `#ef4444` (red-500) | Errors |

## Typography

### Font Family
- **Primary**: Inter (clean, modern, professional)
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Type Scale
| Style | Size | Weight | Line Height | Letter Spacing |
|-------|------|--------|-------------|----------------|
| Display | 72px (4.5rem) | 700 | 1.1 | -0.02em |
| H1 | 56px (3.5rem) | 700 | 1.2 | -0.02em |
| H2 | 40px (2.5rem) | 700 | 1.2 | -0.01em |
| H3 | 32px (2rem) | 600 | 1.3 | -0.01em |
| H4 | 24px (1.5rem) | 600 | 1.4 | 0 |
| Body Large | 20px (1.25rem) | 400 | 1.6 | 0 |
| Body | 16px (1rem) | 400 | 1.6 | 0 |
| Body Small | 14px (0.875rem) | 400 | 1.5 | 0 |
| Caption | 12px (0.75rem) | 500 | 1.5 | 0.02em |

## Spacing System

### 8px Grid
| Token | Value |
|-------|-------|
| space-1 | 4px |
| space-2 | 8px |
| space-3 | 12px |
| space-4 | 16px |
| space-5 | 20px |
| space-6 | 24px |
| space-8 | 32px |
| space-10 | 40px |
| space-12 | 48px |
| space-16 | 64px |
| space-20 | 80px |
| space-24 | 96px |
| space-32 | 128px |

### Section Spacing
- Hero padding: `py-32` (128px)
- Section padding: `py-24` (96px)
- Component gaps: `gap-8` (32px) to `gap-16` (64px)

## Component Library

### Buttons

#### Primary Button
```
- Background: white
- Text: slate-950
- Padding: px-8 py-4
- Border radius: rounded-xl (12px)
- Font: semibold, 16px
- Hover: bg-slate-100, scale-105, shadow-2xl
- Shadow: shadow-indigo-500/25
```

#### Secondary Button
```
- Background: transparent
- Border: 1px solid slate-700
- Text: white
- Padding: px-6 py-3
- Border radius: rounded-xl
- Hover: bg-slate-800, border-slate-600
```

#### Ghost Button
```
- Background: transparent
- Text: slate-400
- Hover: text-white
```

### Cards

#### Feature Card
```
- Background: slate-900/50
- Border: 1px solid slate-800
- Border radius: rounded-2xl (16px)
- Padding: p-6 (24px)
- Hover: border-indigo-500/30
- Transition: colors 200ms
```

#### Pricing Card
```
- Background: slate-900
- Border: 1px solid slate-800
- Featured: border-indigo-500/50, bg-gradient-to-b from-indigo-500/10
- Border radius: rounded-2xl
- Padding: p-8 (32px)
```

#### Testimonial Card
```
- Background: slate-900/30
- Border: 1px solid slate-800/50
- Border radius: rounded-xl
- Padding: p-6
```

### Input Fields
```
- Background: slate-900
- Border: 1px solid slate-800
- Border radius: rounded-lg
- Padding: px-4 py-3
- Focus: border-indigo-500, ring-2 ring-indigo-500/20
- Placeholder: slate-500
```

## Effects & Animations

### Background Effects
- **Gradient orbs**: Blurred circles (blur-3xl) with low opacity (10-20%)
- **Grid pattern**: Subtle dot grid overlay
- **Noise texture**: Optional subtle noise for depth

### Hover Animations
- **Scale**: scale-105 on buttons
- **Glow**: shadow with accent color
- **Border**: Color transition to accent
- **Duration**: 200-300ms
- **Easing**: ease-out

### Scroll Animations
- **Fade up**: opacity 0→1, translateY 20px→0
- **Stagger**: 100ms delay between items
- **Duration**: 600ms
- **Easing**: cubic-bezier(0.16, 1, 0.3, 1)

### Micro-interactions
- **Pulse**: Subtle glow pulse on live indicators
- **Shimmer**: Optional gradient shimmer on featured elements

## Layout

### Container
```
max-width: 1280px (7xl)
padding: px-4 sm:px-6 lg:px-8
margin: mx-auto
```

### Grid System
- 12-column grid
- Gap: 24px (gap-6) to 48px (gap-12)
- Responsive breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)

### Breakpoints
| Name | Width | Usage |
|------|-------|-------|
| sm | 640px | Large phones |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |
| 2xl | 1536px | Large screens |

## Section Specifications

### Navigation
- Fixed position
- Background: transparent → slate-950/80 on scroll (backdrop-blur)
- Height: 80px
- Z-index: 50

### Hero
- Min height: 100vh (minus nav)
- Content: centered
- Max-width: 896px (4xl)

### Social Proof
- Logo strip: grayscale, hover: color
- Trust badges: icon + text

### Features
- Grid: 3 columns on desktop, 1 on mobile
- Icons: 56px container with gradient background

### How It Works
- Numbered steps: large numbers with gradient
- Connection line between steps (desktop)

### Pricing
- 2 columns: Free vs Pro
- Pro card: featured styling with glow

### FAQ
- Accordion style
- Border bottom between items

### Footer
- Multi-column layout
- Social icons
- Newsletter signup

## Assets Required

### Icons (Lucide)
- Bot, Zap, Shield, TrendingUp, Mail, Calendar
- Check, ChevronDown, ChevronRight, Star
- Building2, Target, Users, Sparkles, ArrowRight
- Menu, X (for mobile nav)

### Images
- Hero illustration or dashboard mockup
- Company logos (placeholder for social proof)
- User avatars (testimonials)

### Graphics
- Gradient orbs (CSS)
- Grid pattern (SVG or CSS)

## Accessibility

### Contrast Ratios
- Body text: minimum 4.5:1
- Large text: minimum 3:1
- Interactive elements: minimum 4.5:1

### Focus States
- Visible focus rings on all interactive elements
- Focus ring: 2px offset, indigo-500

### Motion
- Respect `prefers-reduced-motion`
- Essential animations only

## Implementation Notes

### Tailwind Classes Priority
1. Layout (flex, grid, position)
2. Sizing (w, h, max-w)
3. Spacing (p, m, gap)
4. Colors (bg, text, border)
5. Effects (shadow, blur, opacity)
6. Transforms (scale, rotate, translate)
7. Transitions

### Performance
- Use `transform` and `opacity` for animations
- Lazy load below-fold images
- Use `will-change` sparingly

### Responsive Strategy
- Mobile-first approach
- Stack grids on mobile
- Reduce font sizes on smaller screens
- Adjust spacing proportionally
