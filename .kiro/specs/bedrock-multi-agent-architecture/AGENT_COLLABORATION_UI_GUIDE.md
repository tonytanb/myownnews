# Agent Collaboration UI Guide

## Component Overview

The AgentCollaborationTrace component provides a real-time, visually engaging display of multi-agent collaboration in Curio News. This guide explains how the UI works and what users will see.

## Display Modes

### 1. Inline Mode (Default)
Appears automatically in the main content area when:
- Content generation is in progress (`isGenerating = true`)
- Orchestration trace data exists (`orchestrationTrace.length > 0`)

**Location**: Between the audio player and favorite story sections

### 2. Modal Mode
Triggered by clicking the "🤖 Agent Collaboration" button in the provenance section.

**Features**:
- Full-screen overlay with backdrop blur
- Close button (✕) in top-right corner
- Scrollable content for detailed inspection
- Same content as inline mode but with more focus

## Visual Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 Multi-Agent Collaboration                  Total: 5.8s  │
│  Watch our specialized Bedrock agents work together...      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 Phase 1: Analysis ⚡ Parallel              1.50s        │
│  🔄 Analyzing news sources and social impact                │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ 🎯          ✅       │  │ 💡          ✅       │        │
│  │ CONTENT CURATOR      │  │ SOCIAL IMPACT        │        │
│  │ Curating and scoring │  │ Analyzing social...  │        │
│  │ ⏱️ 1.23s            │  │ ⏱️ 0.95s            │        │
│  │ ✨ News curation    │  │ ✨ Social impact    │        │
│  │ 📤 Curated 7 stories│  │ 📤 Scored 7 stories │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                      ↓                                       │
│              Data passed to next phase                       │
│                                                              │
│  ⭐ Phase 2: Story Selection                   0.70s        │
│  🔄 Using Phase 1 outputs to select favorite story          │
│  ┌────────────────────────────────────────────────┐        │
│  │ ⭐                    ✅                       │        │
│  │ STORY SELECTOR                                 │        │
│  │ Selecting the most impactful story             │        │
│  │ ⏱️ 0.70s                                      │        │
│  │ ✨ Favorite story selection and reasoning     │        │
│  │ 📤 Selected: "Climate Breakthrough"           │        │
│  └────────────────────────────────────────────────┘        │
│                      ↓                                       │
│              Data passed to next phase                       │
│                                                              │
│  📝 Phase 3: Script Writing                    1.10s        │
│  🔄 Using selected story to generate script                 │
│  ┌────────────────────────────────────────────────┐        │
│  │ 📝                    ✅                       │        │
│  │ SCRIPT WRITER                                  │        │
│  │ Creating engaging audio script                 │        │
│  │ ⏱️ 1.10s                                      │        │
│  │ ✨ Audio script generation                    │        │
│  │ 📤 Generated 275-word script                  │        │
│  └────────────────────────────────────────────────┘        │
│                      ↓                                       │
│              Data passed to next phase                       │
│                                                              │
│  🎨 Phase 4: Enhancement ⚡ Parallel           2.50s        │
│  🔄 Enhancing content with media and recommendations        │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ 🎉          ✅       │  │ 🎨          ✅       │        │
│  │ ENTERTAINMENT        │  │ MEDIA ENHANCER       │        │
│  │ Curating weekend...  │  │ Enhancing visual...  │        │
│  │ ⏱️ 1.45s            │  │ ⏱️ 1.20s            │        │
│  │ ✨ Weekend recs     │  │ ✨ Visual enhance   │        │
│  │ 📤 5 recommendations │  │ 📤 Enhanced 7 images│        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  🎉 Multi-agent collaboration complete! 6 agents contributed│
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │    6     │  │    4     │  │  1.16s   │  │   100%   │  │
│  │  Agents  │  │  Phases  │  │ Avg Time │  │ Success  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  🔍 Full Transparency    🤝 Agent Collaboration             │
│  Every agent's decision  Agents pass data to each other     │
│  is tracked and visible  for better results                 │
│                                                              │
│  ⚡ Parallel Processing                                     │
│  Multiple agents work simultaneously for speed              │
└─────────────────────────────────────────────────────────────┘
```

## Agent Status Indicators

### Visual States

#### 1. Pending (⏸️)
```
┌──────────────────────┐
│ 🎯          ⏸️      │  ← Paused icon
│ CONTENT CURATOR      │
│ Curating and scoring │
│ (60% opacity)        │  ← Grayed out
└──────────────────────┘
```
- Gray border (#e2e8f0)
- Reduced opacity (0.6)
- No execution time
- Waiting to start

#### 2. In-Progress (⏳)
```
┌──────────────────────┐
│ 🎯          ⏳      │  ← Hourglass icon
│ CONTENT CURATOR      │
│ Curating and scoring │
│ ▓▓▓▓▓▓▓░░░░░░░░░░░  │  ← Animated progress bar
└──────────────────────┘
```
- Blue pulsing border (#667eea)
- Animated progress bar (sliding gradient)
- Pulsing box shadow
- Currently executing

#### 3. Current Agent (⏳ + ACTIVE)
```
┌──────────────────────┐
│ 🎯      ⏳  [ACTIVE] │  ← Special badge
│ CONTENT CURATOR      │
│ Curating and scoring │
│ ▓▓▓▓▓▓▓░░░░░░░░░░░  │  ← Red gradient bar
└──────────────────────┘
```
- Red pulsing border (#ff6b6b)
- "ACTIVE" badge with pulse animation
- Stronger box shadow
- Scaled up slightly (1.02x)

#### 4. Complete (✅)
```
┌──────────────────────┐
│ 🎯          ✅      │  ← Checkmark icon
│ CONTENT CURATOR      │
│ Curating and scoring │
│ ⏱️ 1.23s            │  ← Execution time
│ ✨ News curation    │  ← Attribution
│ 📤 Curated 7 stories│  ← Output summary
└──────────────────────┘
```
- Green border (#48bb78)
- Execution time badge
- Attribution section (gradient background)
- Output summary section
- Fully opaque

#### 5. Failed (❌)
```
┌──────────────────────┐
│ 🎯          ❌      │  ← X icon
│ CONTENT CURATOR      │
│ Curating and scoring │
│ ⚠️ Error occurred   │  ← Error message
└──────────────────────┘
```
- Red border (#f56565)
- Error message displayed
- No execution time
- Indicates failure

## Phase Indicators

### Parallel Execution Badge
```
📊 Phase 1: Analysis ⚡ Parallel    1.50s
```
- Lightning bolt emoji (⚡)
- Red/orange gradient badge
- Indicates agents run simultaneously
- Grid layout with multiple columns

### Sequential Execution
```
⭐ Phase 2: Story Selection    0.70s
```
- No special badge
- Single column layout
- Agents run one after another

### Data Flow Descriptions
Each phase shows what data is being processed:
- Phase 1: "Analyzing news sources and social impact"
- Phase 2: "Using Phase 1 outputs to select favorite story"
- Phase 3: "Using selected story to generate script"
- Phase 4: "Enhancing content with media and recommendations"

### Phase Connectors
```
         ↓
   Data passed to next phase
```
- Vertical line with gradient
- Downward arrow (animated bounce)
- Label explaining data flow
- Appears between all phases

## Statistics Section

### Completion Message
```
🎉 Multi-agent collaboration complete! 6 agents contributed
```
- Green gradient background
- Celebration emoji
- Agent count
- Only shown when complete

### Statistics Grid
```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│    6     │  │    4     │  │  1.16s   │  │   100%   │
│  Agents  │  │  Phases  │  │ Avg Time │  │ Success  │
│ Complete │  │ Executed │  │          │  │   Rate   │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```
- Four stat cards
- Hover effect (lift and shadow)
- Purple accent color
- Monospace font for numbers

## Information Cards

### Three Educational Cards
```
┌─────────────────────────────────────┐
│ 🔍 Full Transparency                │
│ Every agent's decision is tracked   │
│ and visible                         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🤝 Agent Collaboration              │
│ Agents pass data to each other      │
│ for better results                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ⚡ Parallel Processing              │
│ Multiple agents work simultaneously │
│ for speed                           │
└─────────────────────────────────────┘
```
- Light gray background
- Icon + title + description
- Hover effect (lift and shadow)
- Educational content for judges

## Animations

### 1. Progress Bar (In-Progress Agents)
- Sliding gradient animation
- 2-second loop
- Smooth left-to-right motion
- Purple gradient (#667eea → #764ba2)

### 2. Border Pulse (In-Progress Agents)
- Box shadow pulse
- 2-second loop
- Alternates between subtle and prominent
- Blue glow effect

### 3. Current Agent Pulse
- Stronger box shadow pulse
- 1.5-second loop
- Red/orange glow
- Scale animation (1.0 → 1.02)

### 4. Badge Pulse (ACTIVE Badge)
- Scale animation
- 1.5-second loop
- 1.0 → 1.05 → 1.0
- Synchronized with border pulse

### 5. Connector Arrow Bounce
- Vertical bounce animation
- 2-second loop
- 0px → 10px → 0px
- Draws attention to data flow

### 6. Status Indicator Dot
- Opacity and scale pulse
- 1.5-second loop
- White dot on gradient background
- Indicates active generation

## Color Scheme

### Primary Colors
- **Purple Gradient**: `#667eea → #764ba2`
  - Used for: Headers, primary buttons, agent borders (in-progress)
  
- **Red/Orange Gradient**: `#ff6b6b → #ee5a24`
  - Used for: Current agent, parallel badges, accent elements

- **Green Gradient**: `#48bb78 → #38a169`
  - Used for: Complete agents, success messages

### Neutral Colors
- **Light Gray**: `#f7fafc`, `#f8f9fa`
  - Used for: Backgrounds, info cards
  
- **Medium Gray**: `#e2e8f0`, `#cbd5e0`
  - Used for: Borders, dividers
  
- **Dark Gray**: `#718096`, `#4a5568`
  - Used for: Secondary text, descriptions

### Status Colors
- **Pending**: `#cbd5e0` (light gray)
- **In-Progress**: `#667eea` (blue)
- **Current**: `#ff6b6b` (red)
- **Complete**: `#48bb78` (green)
- **Failed**: `#f56565` (red)

## Typography

### Font Families
- **Primary**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'`
- **Monospace**: `'SF Mono', 'Monaco', monospace` (for timing values)

### Font Sizes
- **Main Title**: 2rem (32px)
- **Phase Title**: 1.3rem (20.8px)
- **Agent Name**: 0.9rem (14.4px) - uppercase
- **Body Text**: 0.9rem (14.4px)
- **Small Text**: 0.85rem (13.6px)
- **Tiny Text**: 0.75rem (12px)

### Font Weights
- **Bold**: 700 (titles, agent names)
- **Semi-Bold**: 600 (labels, important text)
- **Medium**: 500 (body text)
- **Regular**: 400 (descriptions)

## Responsive Behavior

### Desktop (> 768px)
- Multi-column grid for parallel agents
- Side-by-side stat cards (4 columns)
- Full-width phase headers
- Comfortable spacing (2.5rem padding)

### Tablet (768px)
- 2-column grid for parallel agents
- 2x2 grid for stat cards
- Reduced spacing (1.5rem padding)
- Adjusted font sizes

### Mobile (< 768px)
- Single column layout
- Stacked stat cards (2 columns)
- Smaller font sizes
- Reduced padding (1rem)
- Touch-friendly tap targets
- Scrollable content

## Accessibility Features

### Semantic HTML
- Proper heading hierarchy (h2, h3, h4)
- Semantic section elements
- Descriptive class names

### Visual Accessibility
- High contrast ratios (WCAG AA compliant)
- Clear status indicators
- Multiple visual cues (color + icon + text)
- Readable font sizes

### Keyboard Navigation
- Focusable interactive elements
- Visible focus states
- Logical tab order

### Screen Readers
- Descriptive text for all visual elements
- Status changes announced
- Meaningful labels

## Usage Examples

### Example 1: Generation Start
```typescript
<AgentCollaborationTrace 
  orchestrationTrace={[]}
  isGenerating={true}
  currentAgent="content_curator"
  showAsModal={false}
/>
```
**Result**: Shows Content Curator as "in-progress" with ACTIVE badge, all others pending

### Example 2: Mid-Generation
```typescript
<AgentCollaborationTrace 
  orchestrationTrace={[
    { agent: 'content_curator', status: 'success', execution_time: 1.23 },
    { agent: 'social_impact_analyzer', status: 'success', execution_time: 0.95 }
  ]}
  isGenerating={true}
  currentAgent="story_selector"
  showAsModal={false}
/>
```
**Result**: First two agents complete, Story Selector in-progress with ACTIVE badge

### Example 3: Complete
```typescript
<AgentCollaborationTrace 
  orchestrationTrace={[
    { agent: 'content_curator', status: 'success', execution_time: 1.23 },
    { agent: 'social_impact_analyzer', status: 'success', execution_time: 0.95 },
    { agent: 'story_selector', status: 'success', execution_time: 0.70 },
    { agent: 'script_writer', status: 'success', execution_time: 1.10 },
    { agent: 'entertainment_curator', status: 'success', execution_time: 1.45 },
    { agent: 'media_enhancer', status: 'success', execution_time: 1.20 }
  ]}
  isGenerating={false}
  currentAgent=""
  showAsModal={false}
/>
```
**Result**: All agents complete, statistics shown, completion message displayed

### Example 4: Modal View
```typescript
<AgentCollaborationTrace 
  orchestrationTrace={completeTrace}
  isGenerating={false}
  currentAgent=""
  onClose={() => setShowModal(false)}
  showAsModal={true}
/>
```
**Result**: Full-screen modal with close button, same content as inline

## Integration with Backend

### Expected Data Format
```typescript
orchestrationTrace: [
  {
    agent: 'content_curator',
    status: 'success' | 'failed' | 'in-progress',
    execution_time: 1.23,
    timestamp: '2025-10-30T21:00:00Z',
    output_summary: 'Curated 7 stories from 15 sources'
  },
  {
    phase: 'Phase 1: Analysis',
    agents: ['content_curator', 'social_impact_analyzer'],
    execution_mode: 'parallel',
    duration: 1.50,
    metadata: { ... }
  }
]
```

### Real-Time Updates
- Component re-renders when `orchestrationTrace` prop changes
- `isGenerating` prop controls generation status indicator
- `currentAgent` prop highlights the active agent
- Smooth transitions between states

## Best Practices

### For Developers
1. Always provide `orchestrationTrace` data for accurate display
2. Update `currentAgent` in real-time during generation
3. Set `isGenerating` to false when complete
4. Include execution times for all completed agents
5. Provide output summaries for better user understanding

### For Designers
1. Maintain consistent spacing (multiples of 0.25rem)
2. Use design system colors for all elements
3. Ensure animations are smooth (60fps)
4. Test on multiple screen sizes
5. Verify color contrast ratios

### For Users
1. Watch the real-time progress during generation
2. Click agent cards for more details (future enhancement)
3. Use modal view for detailed inspection
4. Check statistics for performance metrics
5. Read info cards to understand the system

## Conclusion

The AgentCollaborationTrace component provides a comprehensive, visually engaging, and highly informative display of multi-agent collaboration. It successfully communicates complex AI orchestration in an accessible and beautiful way, making it perfect for demos, user education, and system monitoring.
