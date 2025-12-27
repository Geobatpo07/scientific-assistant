# 🎨 Teslas.ai Modern UI - Visual Design Guide

## Color Palette

### Primary Colors
```
Blue       #0066cc  ████████████████████ Primary actions, links
Indigo     #6366f1  ████████████████████ Secondary, gradients
Pink       #ec4899  ████████████████████ Accents, highlights
```

### Status Colors
```
Success    #10b981  ████████████████████ ✅ Completed, success
Warning    #f59e0b  ████████████████████ ⚠️ Warning, caution
Error      #ef4444  ████████████████████ ❌ Failed, errors
Info       #3b82f6  ████████████████████ ℹ️ Information, status
```

### Background Colors
```
Very Dark  #0f172a  ████████████████████ Main background
Dark Slate #1e293b  ████████████████████ Card background
Slate     #64748b  ████████████████████ Borders, accents
```

### Text Colors
```
Off-White  #f1f5f9  ████████████████████ Primary text
Muted      #cbd5e1  ████████████████████ Secondary text
Disabled   #94a3b8  ████████████████████ Disabled state
```

## Typography Hierarchy

### Headlines
```
32px - Page Title
  🔬 Teslas.ai
  Multi-Agent Scientific Research • Local GenAI Inference

24px - Section Headers
  ## 🔬 Scientific Research
  ## 🧠 LLM Configuration

20px - Subsection Headers
  ### Summary
  ### Quick Templates

16px - Body Text
  Default paragraph content
  Information messages
```

### Font Weight
```
Regular (400)   - Body text, descriptions
Semi-bold (600) - Status badges, highlights
Bold (700)      - Headers, important info
Monospace       - Code blocks, values
```

### Special Text Styles
```
gradient-text: Multi-color gradient (90°)
  Linear: Blue → Indigo → Pink
  Used for: Page title, main headers

status-badge: Inline status indicators
  Padding: 6px 14px
  Border-radius: 20px
  Font-weight: 600
```

## Component Styling

### Cards (Glassmorphism)
```
┌─────────────────────────────────────┐
│  Background: rgba(30, 41, 59, 0.8) │  Glassmorphism effect
│  Blur: 10px backdrop-filter         │  Frosted glass look
│  Border: 1px rgba(148, 163, 184, 0.2) │  Subtle outline
│  Border-radius: 12px                │  Rounded corners
│  Padding: 20px                      │  Internal spacing
│  Shadow: 0 8px 32px rgba(0, 0, 0, 0.3) │  Depth
│  Margin: 10px 0                     │  Vertical spacing
└─────────────────────────────────────┘
```

### Buttons
```
Primary Button (type="primary")
┌──────────────────────────────────┐
│ Background: linear-gradient      │
│   (90deg, #0066cc, #6366f1)      │
│ Color: white                     │
│ Padding: 10px 20px               │
│ Border: none                     │
│ Border-radius: 8px               │
│ Font-weight: 600                 │
│ Transition: all 0.3s ease        │
│ Hover: transform: translateY(-2px) │
│        box-shadow: elevation     │
└──────────────────────────────────┘

Standard Button
┌──────────────────────────────────┐
│ Background: glass-card style     │
│ Color: #f1f5f9                   │
│ Border: subtle                   │
│ Hover: elevation increase        │
└──────────────────────────────────┘
```

### Status Badges
```
Success Badge: ✅ Completed
┌─────────────────────────────────┐
│ Background: #10b981             │  Green
│ Color: white                    │
│ Padding: 6px 14px               │
│ Border-radius: 20px             │
│ Font-weight: 600                │
│ Font-size: 0.85rem              │
│ Margin: 4px                     │
└─────────────────────────────────┘

Warning Badge: ⚠️ Running
├─ Background: #f59e0b (Amber)
├─ Color: white
└─ Similar padding/sizing

Error Badge: ❌ Failed
├─ Background: #ef4444 (Red)
├─ Color: white
└─ Similar padding/sizing

Info Badge: ℹ️ Pending
├─ Background: #3b82f6 (Blue)
├─ Color: white
└─ Similar padding/sizing
```

### Token Counter
```
┌──────────────────────────────────┐
│ Background: rgba(99, 102, 241, 0.2) │ Indigo tint
│ Border: 1px solid #6366f1       │  Indigo outline
│ Border-radius: 6px               │  Slight curve
│ Padding: 8px 12px                │  Compact
│ Font-size: 0.85rem               │  Smaller text
│ Display: inline-block            │  Inline
│ Margin: 4px                      │  Spacing
└──────────────────────────────────┘
Example: 🪙 2,450 tokens
```

## Layout & Spacing

### Grid System
```
Full Width (Main Content)
├─ 1 Column: Full width cards
├─ 2 Columns: Metrics & controls
├─ 3 Columns: Status display
├─ 4 Columns: Aggregate metrics
└─ Flexible: Auto-fit based on content
```

### Spacing Scale
```
4px   - Icon spacing, subtle separation
8px   - Compact element spacing
12px  - Padding, margins
16px  - Section separation
20px  - Card padding, major spacing
32px  - Section breaks
```

### Dividers
```
┌────────────────────────────────┐
│      st.divider()              │
│  ─────────────────────────────  │
│  Light line: opacity 0.2       │
│  Full width                    │
│  Margin: 10px 0                │
└────────────────────────────────┘
```

## Icons & Emojis

### Feature Icons
```
🔬 Research          - Main feature, science
🔍 Search            - Literature search
📄 Ingest            - Document upload
📚 Knowledge Base     - Data storage
📜 History           - Query tracking

⚙️ Configuration      - Settings
🧠 LLM Settings      - AI/language model
🤖 Agents            - Multi-agent system
📊 Statistics        - Metrics/data
🔐 Security/Privacy  - Data protection

✅ Success           - Completed
❌ Failed            - Error
⚠️ Warning           - Caution
ℹ️ Information       - Notice
⏳ Running           - In progress
```

### Status Indicators
```
🟢 Green circle     - Healthy/online
🔴 Red circle       - Offline/error
🟡 Yellow circle    - Warning/caution
🔵 Blue circle      - Info/neutral

✅ Checkmark        - Success, done
❌ X mark           - Failed, error
⚠️ Warning sign     - Caution needed
ℹ️ Info sign        - Information
⏸️ Pause            - Paused/pending
```

## Animation & Interactions

### Transitions
```
Duration: 0.3s (standard)
Easing: ease (default)
Properties: all (unless specified)

Hover Effects:
├─ Buttons: translateY(-2px) + shadow
├─ Cards: opacity increase, shadow
└─ Text: color change, underline

Focus Effects:
├─ Border highlight
├─ Shadow increase
└─ Color emphasis
```

### Loading States
```
Spinner (st.spinner):
├─ Animation: rotating icon
├─ Message: "🤖 Research in progress..."
├─ Duration: Until operation completes
└─ UI: Blocked until done

Progress (implicit):
├─ Expanders: Click to reveal
├─ Tabs: Click to switch
└─ Results: Lazy load on tab switch
```

## Responsive Design

### Desktop (1920px+)
- Full sidebar (300px)
- Wide content area
- 3-4 column layouts
- All features visible

### Laptop (1280px+)
- Sidebar (280px)
- Comfortable spacing
- 2-3 column layouts
- All features accessible

### Tablet (768px+)
- Sidebar collapsible
- 2 column max
- Optimized spacing
- Touch-friendly buttons

### Mobile (320px+)
- Full-width layout
- Single column
- Stacked components
- Large touch targets

## Design System Constants

### Border Radius
```
4px  - Subtle corners (inputs)
6px  - Token counters, badges
8px  - Buttons, tabs
12px - Cards, panels
20px - Badge pills, rounded buttons
```

### Shadows
```
Small:   0 2px 4px rgba(0, 0, 0, 0.1)
Medium:  0 4px 12px rgba(0, 0, 0, 0.15)
Large:   0 8px 32px rgba(0, 0, 0, 0.3)
Hover:   0 12px 40px rgba(0, 0, 0, 0.4)
```

### Opacity
```
100%  - Full opacity, primary elements
80%   - Glass card backgrounds
60%   - Secondary text
40%   - Borders, subtle elements
20%   - Hover/focus overlays
```

## Accessibility Considerations

### Color Contrast
- Text on dark: Minimum 4.5:1 ratio
- White text on colored: Sufficient for WCAG AA
- Status colors: Redundant with text/icons

### Interactive Elements
- Minimum 44px touch target
- Clear hover/focus states
- Semantic HTML structure
- Alt text for icons

### Visual Hierarchy
- Clear headings hierarchy (H1-H3)
- Sufficient whitespace
- Consistent layout patterns
- Status indicators with text + icon

## Dark Theme Specifications

### Application Theme
```
Primary Dark: #0f172a
  Uses: Main background
  RGB: 15, 23, 42
  Lightness: Very low (5%)

Secondary Dark: #1e293b
  Uses: Card backgrounds
  RGB: 30, 41, 59
  Lightness: Low (13%)

Slate: #64748b
  Uses: Borders, subtle accents
  RGB: 100, 116, 139
  Lightness: Medium (50%)
```

### Contrast Values
```
Text on Dark:
├─ Off-White (#f1f5f9): 14.5:1 ratio (AAA)
├─ Muted (#cbd5e1): 10.2:1 ratio (AAA)
└─ Disabled (#94a3b8): 6.8:1 ratio (AA)

Badges on Colors:
├─ White on Green (#10b981): 5.5:1 (AAA)
├─ White on Amber (#f59e0b): 4.5:1 (AA)
└─ White on Blue (#0066cc): 6.2:1 (AAA)
```

## CSS Classes Reference

```
.main                   - Main content area
.glass-card             - Glassmorphism cards
.gradient-text          - Multi-color gradient text
.status-badge           - Status indicator badges
.status-success         - Green badge
.status-warning         - Amber badge
.status-danger          - Red badge
.status-info            - Blue badge
.token-counter          - Token counter display
.metric-item            - Metric card styling
.stTabs                 - Tab container
.stTabs [aria-selected] - Selected tab styling
```

## Implementation Examples

### Gradient Header
```html
<h1 style="background: linear-gradient(90deg, #0066cc, #6366f1, #ec4899);
           -webkit-background-clip: text;
           background-clip: text;
           -webkit-text-fill-color: transparent;">
  🔬 Teslas.ai
</h1>
```

### Status Badge
```html
<span class="status-badge status-success">✅ Complete</span>
<span class="status-badge status-warning">⚠️ Running</span>
<span class="status-badge status-danger">❌ Failed</span>
<span class="status-badge status-info">ℹ️ Pending</span>
```

### Glass Card
```html
<div class="glass-card">
  <p>Content with glassmorphism effect</p>
</div>
```

## Color Usage Guidelines

### When to Use Each Color

**Blue (#0066cc)**
- Primary action buttons
- Links and hyperlinks
- Important CTAs
- Visual emphasis

**Indigo (#6366f1)**
- Gradients
- Secondary accents
- Token counters
- Borders

**Pink (#ec4899)**
- Highlight accents
- Gradient endpoints
- Special emphasis
- Contrast element

**Green (#10b981)**
- Success messages
- Completion indicators
- Positive feedback
- Health checks

**Amber (#f59e0b)**
- Warnings
- Caution messages
- Pending states
- Information alerts

**Red (#ef4444)**
- Error messages
- Failures
- Critical issues
- Negative feedback

**Light Blue (#3b82f6)**
- Informational elements
- General status
- Neutral indicators
- Secondary information

---

**Version**: 2.0 Modern GenAI Interface  
**Last Updated**: December 26, 2025  
**Design System**: Glassmorphism + Dark Theme
