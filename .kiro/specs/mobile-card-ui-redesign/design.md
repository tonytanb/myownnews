# Design Document: Mobile Card UI Redesign

## Overview

Transform Curio from a traditional scrollable news feed into an immersive, mobile-first card-based experience. The new UI will feature full-screen swipeable story cards with video backgrounds, smooth Framer Motion animations, and a social media-inspired interaction model. Each card represents a single story with 15-30 seconds of content, optimized for quick consumption by Gen Z users.

## Architecture

### Component Hierarchy

```
App.tsx (Root)
├── CurioCardStack (NEW - Main Container)
│   ├── OverviewCard (NEW - First card)
│   ├── StoryCard[] (NEW - Individual story cards)
│   │   ├── BackgroundMedia (video/image/GIF)
│   │   ├── CategoryTag
│   │   ├── StoryContent
│   │   ├── AudioButton
│   │   └── NavigationDots
│   └── CardTransition (Framer Motion wrapper)
├── AudioPlayer (Modified - Embedded in cards)
└── AgentTrace (Existing - Analytics overlay)
```

### Data Flow

```
1. Bootstrap API → Bedrock Agent Outputs
2. Content Curator → curated_stories[] → Card Data
3. Story Selector → favorite_story → First Story Card
4. Script Writer → script + word_timings → Per-Card Scripts (15-30s segments)
5. Media Enhancer → media_enhancements → Video/Image/GIF Backgrounds
6. Entertainment Curator → entertainment_recommendations → Weekend Cards
```

## Components and Interfaces

### 1. CurioCardStack Component

**Purpose**: Main container managing card state, navigation, and transitions

**Props**:
```typescript
interface CurioCardStackProps {
  newsItems: NewsItem[];
  agentOutputs: AgentOutputs;
  script: string;
  wordTimings: WordTiming[];
  onAudioPlay: (cardIndex: number) => void;
}
```

**State**:
```typescript
interface CardStackState {
  currentCardIndex: number;
  cards: StoryCard[];
  isTransitioning: boolean;
  preloadedMedia: Map<number, HTMLVideoElement | HTMLImageElement>;
}
```

**Key Methods**:
- `nextCard()`: Advance to next card with animation
- `previousCard()`: Go back to previous card
- `preloadNextMedia()`: Preload media for next 2 cards
- `handleSwipe()`: Handle touch/swipe gestures

### 2. OverviewCard Component

**Purpose**: First card showing daily summary and story highlights

**Props**:
```typescript
interface OverviewCardProps {
  date: string;
  highlights: string[];
  totalStories: number;
  backgroundImage: string;
  onTap: () => void;
}
```

**Layout**:
- Centered content with Sparkles icon
- "Today in Curio 🪄" title
- Date in long format
- 4-6 emoji-prefixed highlights
- "Tap to begin →" CTA

### 3. StoryCard Component

**Purpose**: Individual story card with media background and content

**Props**:
```typescript
interface StoryCardProps {
  story: NewsItem;
  categoryType: CategoryType;
  scriptSegment: string;
  estimatedDuration: number;
  mediaUrl: string;
  mediaType: 'video' | 'image' | 'gif';
  onAudioPlay: () => void;
  onTap: () => void;
}
```

**Layout Structure**:
```
┌─────────────────────────────┐
│ [curio]            [Tag]    │ ← Top bar
│                             │
│                             │
│    Background Media         │
│    (video/image/GIF)        │
│    with gradient overlay    │
│                             │
│                             │
│  ┌─────────────────────┐   │
│  │ Story Title         │   │ ← Content area
│  │ Summary text...     │   │
│  └─────────────────────┘   │
│                             │
│  [🔊] Tap to listen         │ ← Audio button
│  ● ○ ○ ○ ○                 │ ← Navigation dots
└─────────────────────────────┘
```

### 4. BackgroundMedia Component

**Purpose**: Render video, image, or GIF backgrounds with fallbacks

**Props**:
```typescript
interface BackgroundMediaProps {
  mediaUrl: string;
  mediaType: 'video' | 'image' | 'gif';
  fallbackImage: string;
  alt: string;
}
```

**Behavior**:
- Videos: autoplay, muted, loop, playsInline
- Images: object-fit cover with brightness filter
- GIFs: treated as images with animation
- Fallback: Unsplash category image if media fails

### 5. CategoryTag Component

**Purpose**: Visual badge showing story category with gradient and icon

**Props**:
```typescript
interface CategoryTagProps {
  category: CategoryType;
}

type CategoryType = 'favorite' | 'world' | 'local' | 'event' | 'movie' | 'music' | 'book';
```

**Category Styling**:
```typescript
const categoryConfig = {
  favorite: { 
    gradient: 'from-pink-500 to-rose-500', 
    icon: <Heart />,
    label: 'FAVORITE'
  },
  world: { 
    gradient: 'from-blue-500 to-indigo-500', 
    icon: <Globe />,
    label: 'WORLD'
  },
  local: { 
    gradient: 'from-green-500 to-emerald-500', 
    icon: <MapPin />,
    label: 'LOCAL'
  },
  // ... etc
};
```

## Data Models

### StoryCard Data Structure

```typescript
interface StoryCard {
  id: number;
  type: 'overview' | CategoryType;
  title: string;
  summary: string;
  scriptSegment: string;
  estimatedDuration: number; // seconds
  mediaUrl: string;
  mediaType: 'video' | 'image' | 'gif';
  fallbackImage: string;
  category: string;
  source: string;
  audioTimestamp: number; // Start time in full audio
}
```

### Agent Output Mapping

```typescript
interface AgentOutputMapping {
  // Content Curator → Card structure
  curatedStories: NewsItem[] → StoryCard[];
  
  // Story Selector → First story card
  favoriteStory: FavoriteStory → StoryCard[0];
  
  // Script Writer → Per-card scripts
  script: string → scriptSegments: string[];
  wordTimings: WordTiming[] → cardDurations: number[];
  
  // Media Enhancer → Background media
  mediaEnhancements: MediaEnhancement[] → {
    mediaUrl: string;
    mediaType: 'video' | 'image' | 'gif';
  }[];
  
  // Entertainment Curator → Weekend cards
  entertainmentRecommendations: Entertainment → StoryCard[];
}
```

### Script Segmentation Algorithm

```typescript
function segmentScript(
  script: string, 
  wordTimings: WordTiming[], 
  targetDuration: number = 25 // seconds
): ScriptSegment[] {
  const segments: ScriptSegment[] = [];
  let currentSegment = '';
  let currentDuration = 0;
  let startTime = 0;
  
  for (const timing of wordTimings) {
    currentSegment += timing.word + ' ';
    currentDuration = timing.end - startTime;
    
    // Split at sentence boundaries when approaching target duration
    if (currentDuration >= targetDuration && isSentenceEnd(timing.word)) {
      segments.push({
        text: currentSegment.trim(),
        duration: currentDuration,
        startTime: startTime,
        endTime: timing.end
      });
      
      currentSegment = '';
      startTime = timing.end;
      currentDuration = 0;
    }
  }
  
  // Add remaining segment
  if (currentSegment.trim()) {
    segments.push({
      text: currentSegment.trim(),
      duration: currentDuration,
      startTime: startTime,
      endTime: wordTimings[wordTimings.length - 1].end
    });
  }
  
  return segments;
}
```

## Animations and Transitions

### Framer Motion Configuration

```typescript
const cardVariants = {
  enter: {
    opacity: 0,
    y: 50,
    scale: 0.95
  },
  center: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1] // Custom easing
    }
  },
  exit: {
    opacity: 0,
    y: -50,
    scale: 0.95,
    transition: {
      duration: 0.3
    }
  }
};

const overviewContentVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delay: 0.3,
      duration: 0.5
    }
  }
};
```

### Gesture Handling

```typescript
const swipeConfig = {
  onSwipeLeft: () => nextCard(),
  onSwipeRight: () => previousCard(),
  swipeThreshold: 50, // pixels
  swipeVelocityThreshold: 0.5
};
```

## Media Strategy

### Media Source Priority

1. **Primary**: Media Enhancer agent output
   - Videos from agent's media search
   - High-quality images from agent curation
   - GIFs for dynamic content

2. **Secondary**: Unsplash API
   - Category-based image search
   - Deterministic URLs using title hash
   - Format: `https://source.unsplash.com/800x400/?{keywords}&sig={hash}`

3. **Tertiary**: Placeholder
   - Colored gradient with category emoji
   - Format: `https://via.placeholder.com/800x400/{color}/ffffff?text=News`

### Media Preloading Strategy

```typescript
function preloadMedia(cards: StoryCard[], currentIndex: number): void {
  const preloadRange = [currentIndex + 1, currentIndex + 2];
  
  preloadRange.forEach(index => {
    if (index < cards.length) {
      const card = cards[index];
      
      if (card.mediaType === 'video') {
        const video = document.createElement('video');
        video.src = card.mediaUrl;
        video.preload = 'auto';
        video.load();
      } else {
        const img = new Image();
        img.src = card.mediaUrl;
      }
    }
  });
}
```

## Integration with Existing Systems

### API Integration

**Existing Endpoint**: `/bootstrap`
- Returns: `{ news_items, script, word_timings, agentOutputs }`
- No changes needed to backend
- Frontend transforms data into card format

**Data Transformation**:
```typescript
function transformToCards(bootstrapData: BootstrapResponse): StoryCard[] {
  const cards: StoryCard[] = [];
  
  // 1. Create overview card
  cards.push(createOverviewCard(bootstrapData));
  
  // 2. Create favorite story card (first)
  if (bootstrapData.agentOutputs?.favoriteStory) {
    cards.push(createFavoriteCard(
      bootstrapData.agentOutputs.favoriteStory,
      bootstrapData.script,
      bootstrapData.wordTimings
    ));
  }
  
  // 3. Create story cards from curated news
  const scriptSegments = segmentScript(
    bootstrapData.script,
    bootstrapData.wordTimings
  );
  
  bootstrapData.news_items.forEach((item, index) => {
    cards.push(createStoryCard(
      item,
      scriptSegments[index],
      bootstrapData.agentOutputs?.mediaEnhancements
    ));
  });
  
  // 4. Create entertainment cards
  if (bootstrapData.agentOutputs?.weekendRecommendations) {
    cards.push(...createEntertainmentCards(
      bootstrapData.agentOutputs.weekendRecommendations
    ));
  }
  
  return cards;
}
```

### Audio Player Integration

**Current**: Standalone AudioPlayer component
**New**: Embedded audio controls in each card

**Changes**:
- Audio button triggers playback from card's timestamp
- Global audio state managed by CurioCardStack
- Sync card transitions with audio progress
- Auto-advance to next card when audio segment ends

```typescript
interface AudioState {
  isPlaying: boolean;
  currentCardIndex: number;
  audioElement: HTMLAudioElement;
  currentTime: number;
}

function handleAudioPlay(cardIndex: number): void {
  const card = cards[cardIndex];
  audioElement.currentTime = card.audioTimestamp;
  audioElement.play();
  
  // Auto-advance when segment ends
  const segmentEndTime = card.audioTimestamp + card.estimatedDuration;
  const checkInterval = setInterval(() => {
    if (audioElement.currentTime >= segmentEndTime) {
      clearInterval(checkInterval);
      nextCard();
    }
  }, 100);
}
```

## Responsive Design

### Mobile-First Approach

**Primary Target**: 380px × 680px (iPhone SE / small Android)
**Secondary**: 390px × 844px (iPhone 14)
**Tertiary**: 428px × 926px (iPhone 14 Pro Max)

### Desktop Adaptation

```css
.curio-card-stack {
  /* Mobile: Full screen */
  width: 100vw;
  height: 100vh;
}

@media (min-width: 768px) {
  /* Desktop: Centered card */
  .curio-card-stack {
    width: 380px;
    height: 680px;
    margin: 0 auto;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  }
  
  .app-background {
    background: #000;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }
}
```

## Performance Optimization

### Key Metrics

- **Target Load Time**: < 2 seconds to first card
- **Target Transition Time**: 500ms per card
- **Target Media Load**: < 1 second per video/image
- **Memory Budget**: < 100MB for 10 cards

### Optimization Strategies

1. **Lazy Loading**: Only render current card + adjacent cards
2. **Media Preloading**: Preload next 2 cards' media
3. **Virtual Scrolling**: Unload cards > 3 positions away
4. **Image Optimization**: Use WebP format, 800x400 max resolution
5. **Video Optimization**: Use MP4 H.264, 720p max, < 5MB per video

### Code Splitting

```typescript
// Lazy load card components
const OverviewCard = lazy(() => import('./components/OverviewCard'));
const StoryCard = lazy(() => import('./components/StoryCard'));
const EntertainmentCard = lazy(() => import('./components/EntertainmentCard'));
```

## Error Handling

### Media Loading Errors

```typescript
function handleMediaError(card: StoryCard): void {
  // Try fallback image
  if (card.fallbackImage) {
    card.mediaUrl = card.fallbackImage;
    card.mediaType = 'image';
  } else {
    // Generate Unsplash fallback
    card.mediaUrl = generateUnsplashUrl(card.category, card.title);
    card.mediaType = 'image';
  }
}
```

### Script Segmentation Errors

```typescript
function handleScriptError(newsItems: NewsItem[]): ScriptSegment[] {
  // Fallback: Create simple segments from summaries
  return newsItems.map((item, index) => ({
    text: `${item.title}. ${item.summary}`,
    duration: 20, // Default 20 seconds
    startTime: index * 20,
    endTime: (index + 1) * 20
  }));
}
```

## Accessibility

### WCAG 2.1 AA Compliance

1. **Contrast Ratios**: 
   - Text on backgrounds: minimum 4.5:1
   - Gradient overlays ensure readability
   - Category tags: white text on colored backgrounds

2. **Keyboard Navigation**:
   - Arrow keys: Navigate between cards
   - Space/Enter: Play audio
   - Escape: Close modals

3. **Screen Reader Support**:
   - ARIA labels for all interactive elements
   - Announce card transitions
   - Describe media content

4. **Touch Targets**:
   - Minimum 44px × 44px for all buttons
   - Audio button: 48px × 48px
   - Swipe gestures with visual feedback

## Testing Strategy

### Unit Tests

- Component rendering with various props
- Script segmentation algorithm
- Media preloading logic
- Category mapping functions

### Integration Tests

- Card navigation flow
- Audio playback synchronization
- Media loading and fallbacks
- Agent output transformation

### E2E Tests

- Complete user journey from overview to last card
- Swipe gestures on mobile devices
- Audio playback across cards
- Error recovery scenarios

### Performance Tests

- Lighthouse score > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Memory usage < 100MB

## Migration Strategy

### Phase 1: Parallel Implementation (Week 1)

- Create new components alongside existing UI
- Feature flag: `ENABLE_CARD_UI`
- A/B test with 10% of users

### Phase 2: Refinement (Week 2)

- Gather user feedback
- Optimize animations and transitions
- Fix edge cases and bugs

### Phase 3: Full Rollout (Week 3)

- Enable for 100% of users
- Remove old UI components
- Monitor analytics and performance

### Rollback Plan

- Keep old UI components for 2 weeks
- Feature flag allows instant rollback
- Database stores user preference

## Dependencies

### New Libraries

```json
{
  "framer-motion": "^10.16.4",
  "lucide-react": "^0.292.0",
  "react-swipeable": "^7.0.1"
}
```

### Existing Libraries (No Changes)

- React 18
- TypeScript
- Axios
- AWS SDK

## Future Enhancements

1. **Personalization**: ML-based card ordering
2. **Social Sharing**: Share individual cards
3. **Bookmarking**: Save favorite stories
4. **Dark/Light Mode**: Theme switching
5. **Offline Mode**: Cache cards for offline viewing
6. **Voice Commands**: "Next story", "Play audio"
7. **Haptic Feedback**: Vibration on card transitions (mobile)
8. **3D Effects**: Parallax scrolling, depth effects
