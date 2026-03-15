# ACQUISITOR Assets

## Icons (Lucide React)

All icons are imported from `lucide-react` package:

### Hero Section
- `Zap` - Logo and CTA icons
- `Bot` - Dashboard mockup AI agent
- `Building2` - Business listings
- `ArrowRight` - CTA button

### Features Section
- `Bot` - AI Discovery Agent feature
- `Target` - Smart Scoring feature  
- `MessageSquare` - Autonomous Outreach feature
- `BarChart3` - Pipeline Analytics feature

### How It Works Section
- `Users` - Step 1: Tell Your Story
- `Sparkles` - Step 2: Agent Goes to Work
- `Calendar` - Step 3: Approve & Connect

### Navigation
- `Menu` - Mobile menu open
- `X` - Mobile menu close

### Pricing Section
- `Check` - Feature checkmarks

### Testimonials Section
- `Star` - Rating stars
- `Quote` - Decorative quote icon

### FAQ Section
- `ChevronDown` - Closed accordion state
- `ChevronUp` - Open accordion state

## Installation

All icons come from the `lucide-react` package which should already be installed:

```bash
npm install lucide-react
```

## CSS/Tailwind Features Used

### Gradients
- `bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500` - Logo, CTA buttons
- `bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400` - Hero headline accent
- `from-indigo-500 to-blue-500` - Feature card 1
- `from-purple-500 to-pink-500` - Feature card 2
- `from-pink-500 to-rose-500` - Feature card 3
- `from-emerald-500 to-teal-500` - Feature card 4

### Background Effects
- `blur-[120px]` - Large gradient orbs
- `bg-indigo-500/10` - Subtle colored backgrounds
- CSS grid pattern (embedded in JSX) - Subtle background texture

### Shadows
- `shadow-2xl shadow-indigo-500/10` - Card glows
- `shadow-lg shadow-indigo-500/20` - Button/icon glows
- `shadow-indigo-500/25` - Hover button glows

### No External Images Required

The landing page uses:
1. CSS-generated visual effects (gradients, blurs)
2. Lucide icons for all iconography
3. Text-based company logos (initials in styled boxes)
4. Generated avatar initials for testimonials
5. CSS-based dashboard mockup (no screenshot needed)

This ensures:
- Fast loading (no image downloads)
- Crisp rendering at all resolutions
- No external dependencies
- Small bundle size
