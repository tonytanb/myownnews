# Production Polish Design

## Overview

This design transforms Curio News from a demo application to a production-ready news product by:
1. Removing all demo-specific language and replacing with product messaging
2. Fixing audio playback issues by ensuring proper audio URL handling
3. Cleaning the interactive transcript to show only the actual news script
4. Ensuring all news items display images through fallback mechanisms
5. Moving analytics and performance data to a separate menu-accessible screen

## Architecture

### Component Structure

```
App.tsx (Main Container)
├── Header
│   ├── Logo
│   ├── Menu Button (NEW)
│   │   └── Dropdown Menu
│   │       ├── Analytics
│   │       └── About
│   └── Agent Status (conditional)
├── Main Content (Landing Page)
│   ├── Date Header
│   ├── Title Section ("Today's Brief")
│   ├── Audio Section ("Listen to Today's Brief")
│   │   └── AudioPlayer Component
│   ├── Favorite Story
│   ├── News Grid
│   │   └── NewsItems (with image fallbacks)
│   ├── Interactive Transcript (cleaned)
│   └── Weekend Recommendations
└── Analytics Screen (NEW - separate route/view)
    ├── Back Button
    ├── Agent Provenance Section
    ├── Agent Collaboration Trace
    ├── Performance Metrics
    └── Debugging Dashboard
```

## Components and Interfaces

### 1. Text Content Updates

**Location**: `App.tsx`, `AudioPlayer.tsx`

**Changes**:
- Replace "🎧 Agent-Powered News Demo" → "🎧 Listen to Today's Brief"
- Remove "Click below to experience our AI-curated news briefing with full provenance tracking"
- Update any "demo" references to product language

### 2. Audio Player Fix

**Location**: `AudioPlayer.tsx`, `main_handler.py`

**Problem**: Audio URL is not being properly generated or passed to the frontend

**Solution**:
- Verify `audioUrl` field in bootstrap response
- Check if audio generation is being triggered
- Ensure Polly synthesis is working
- Add fallback to pre-generated sample audio if generation fails
- Display loading state while audio is being generated

**Interface**:
```typescript
interface AudioPlayerProps {
  onContentUpdate: (data: any) => void;
  onTimeUpdate: (time: number) => void;
}

interface AudioState {
  audioUrl: string | null;
  isLoading: boolean;
  error: string | null;
  isPlaying: boolean;
}
```

### 3. Interactive Transcript Cleanup

**Location**: `InteractiveTranscript.tsx`

**Problem**: Script contains prompt text like "*opens with an upbeat, conversational tone*"

**Solution**:
- Add script cleaning function to remove stage directions
- Filter out text within asterisks: `*...*`
- Remove prompt instructions before displaying
- Trim whitespace and normalize spacing

**Implementation**:
```typescript
function cleanScript(rawScript: string): string {
  // Remove stage directions in asterisks
  let cleaned = rawScript.replace(/\*[^*]+\*/g, '');
  
  // Remove common prompt phrases
  cleaned = cleaned.replace(/^(Hey fam,?|Welcome back to|Hi everyone,?)/i, '');
  
  // Normalize whitespace
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  
  return cleaned;
}
```

### 4. News Item Image Fallbacks

**Location**: `NewsItems.tsx`, `multi_agent_orchestrator.py`

**Problem**: Only first 3 news items have images

**Solution**:
- Backend: Ensure all news items get image URLs from NewsAPI or generate Unsplash fallbacks
- Frontend: Add fallback image generation for any missing images
- Use category-based Unsplash URLs: `https://source.unsplash.com/800x400/?{category},news`

**Backend Enhancement** (`multi_agent_orchestrator.py`):
```python
def ensure_news_images(news_items):
    """Ensure all news items have images"""
    for item in news_items:
        if not item.get('image') or item['image'] == '':
            category = item.get('category', 'news').lower()
            # Generate Unsplash fallback
            item['image'] = f"https://source.unsplash.com/800x400/?{category},news,{item.get('title', '')[:20]}"
    return news_items
```

**Frontend Enhancement** (`NewsItems.tsx`):
```typescript
function getNewsImage(item: NewsItem): string {
  if (item.image && item.image !== '') {
    return item.image;
  }
  
  // Fallback to Unsplash with category
  const category = item.category?.toLowerCase() || 'news';
  const keywords = item.title.split(' ').slice(0, 3).join(',');
  return `https://source.unsplash.com/800x400/?${category},${keywords}`;
}
```

### 5. Analytics Screen Separation

**Location**: New `AnalyticsScreen.tsx`, `App.tsx`

**Implementation**:

**Option A: Modal Overlay** (Simpler, no routing needed)
```typescript
// App.tsx
const [showAnalyticsScreen, setShowAnalyticsScreen] = useState(false);

// Header menu
<Menu>
  <MenuItem onClick={() => setShowAnalyticsScreen(true)}>
    📊 Analytics
  </MenuItem>
</Menu>

// Conditional render
{showAnalyticsScreen && (
  <AnalyticsScreen 
    onClose={() => setShowAnalyticsScreen(false)}
    traceId={traceId}
    orchestrationTrace={orchestrationTrace}
    agentOutputs={agentOutputs}
  />
)}
```

**Option B: React Router** (More scalable)
```typescript
// App.tsx with routing
<BrowserRouter>
  <Routes>
    <Route path="/" element={<MainPage />} />
    <Route path="/analytics" element={<AnalyticsScreen />} />
  </Routes>
</BrowserRouter>
```

**Recommendation**: Use Option A (Modal Overlay) for faster implementation

**AnalyticsScreen Component**:
```typescript
interface AnalyticsScreenProps {
  onClose: () => void;
  traceId: string;
  orchestrationTrace: any[];
  agentOutputs: any;
}

const AnalyticsScreen: React.FC<AnalyticsScreenProps> = ({
  onClose,
  traceId,
  orchestrationTrace,
  agentOutputs
}) => {
  return (
    <div className="analytics-screen-overlay">
      <div className="analytics-screen-container">
        <header className="analytics-header">
          <button onClick={onClose}>← Back to News</button>
          <h1>📊 Analytics & Agent Insights</h1>
        </header>
        
        <div className="analytics-content">
          {/* Agent Provenance Section */}
          <section className="provenance-section">
            {/* ... existing provenance content ... */}
          </section>
          
          {/* Agent Collaboration */}
          <section className="collaboration-section">
            <AgentCollaborationTrace 
              orchestrationTrace={orchestrationTrace}
              showAsModal={false}
            />
          </section>
          
          {/* Performance Metrics */}
          <section className="metrics-section">
            <PerformanceMonitor />
          </section>
          
          {/* Debugging Dashboard */}
          <section className="debugging-section">
            <DebuggingDashboard onClose={() => {}} />
          </section>
        </div>
      </div>
    </div>
  );
};
```

## Data Models

### Audio Response
```typescript
interface AudioResponse {
  audioUrl: string;
  script: string;
  word_timings: WordTiming[];
  generatedAt: string;
  sources: string[];
}
```

### News Item (Enhanced)
```typescript
interface NewsItem {
  title: string;
  category: string;
  summary: string;
  full_text?: string;
  image: string;  // Now required, with fallback
  relevance_score?: number;
  source?: string;
  link?: string;
}
```

## Error Handling

### Audio Playback Errors
- **No Audio URL**: Display "Generating your personalized news briefing..." with spinner
- **Audio Load Error**: Display "Unable to load audio. Please try refreshing." with retry button
- **Polly Synthesis Error**: Fall back to text-only mode with clear message

### Image Loading Errors
- **Image 404**: Automatically switch to Unsplash fallback
- **Unsplash Failure**: Display styled placeholder with category icon
- **Network Error**: Show placeholder with retry option

### Analytics Screen Errors
- **No Data Available**: Display "Analytics data is being collected..." message
- **Trace Loading Error**: Show error message with option to return to main page

## Testing Strategy

### Unit Tests
1. `cleanScript()` function removes all stage directions
2. `getNewsImage()` generates proper fallback URLs
3. Audio player handles missing URL gracefully
4. Analytics screen renders without data

### Integration Tests
1. Audio playback works end-to-end
2. All 7 news items display with images
3. Transcript displays cleaned script
4. Analytics screen accessible from menu
5. Navigation between main page and analytics works

### Manual Testing
1. Verify no "demo" language appears on main page
2. Click play button and confirm audio plays
3. Check all news cards have images
4. Open analytics screen and verify all sections load
5. Test on mobile devices for responsive behavior

## Performance Considerations

### Image Loading
- Use lazy loading for news item images
- Implement image caching
- Optimize Unsplash URLs with size parameters

### Analytics Screen
- Load analytics data only when screen is opened
- Implement pagination for large trace logs
- Cache analytics data to avoid re-fetching

### Audio Streaming
- Use progressive loading for audio files
- Implement audio buffering indicators
- Cache audio files in browser storage

## Accessibility

- Ensure menu button has proper ARIA labels
- Analytics screen should be keyboard navigable
- Audio player controls must be accessible
- Image alt text should be descriptive
- Focus management when opening/closing analytics screen
