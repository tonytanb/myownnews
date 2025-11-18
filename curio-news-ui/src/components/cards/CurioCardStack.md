# CurioCardStack Component

## Overview

The `CurioCardStack` component is the main container for the mobile-first card-based UI. It manages card state, navigation, animations, and gesture handling for a swipeable story experience.

## Features

### State Management (Task 7.1)
- **Current Card Index**: Tracks which card is currently displayed
- **Cards Array**: Stores all transformed story cards from bootstrap data
- **Transition State**: Prevents rapid navigation during animations
- **Preloaded Media**: Tracks preloaded media for smooth transitions

### Card Navigation (Task 7.2)
- **Next/Previous Card**: Navigate through cards with smooth animations
- **Keyboard Navigation**: Arrow keys (←/→ or ↑/↓) to navigate
- **Tap/Click to Advance**: Tap anywhere on the card to move forward
- **Transition Locking**: Prevents navigation during animations (500ms)

### Framer Motion Animations (Task 7.3)
- **Enter Animation**: Cards fade in from bottom (y: 50) with scale (0.95)
- **Center Animation**: Cards animate to full opacity and scale (1.0)
- **Exit Animation**: Cards fade out to top (y: -50) with scale (0.95)
- **Custom Easing**: Smooth cubic-bezier curve [0.4, 0, 0.2, 1]
- **Duration**: 500ms for enter/center, 300ms for exit

### Swipe Gesture Handling (Task 7.4)
- **Swipe Left**: Navigate to next card
- **Swipe Right**: Navigate to previous card
- **Swipe Threshold**: 50px minimum distance
- **Mouse Support**: Desktop testing with mouse drag

## Usage

```tsx
import { CurioCardStack } from './components/cards';
import { BootstrapResponse } from './components/cards/types';

function App() {
  const [bootstrapData, setBootstrapData] = useState<BootstrapResponse | null>(null);

  const handleAudioPlay = (cardIndex: number, timestamp: number) => {
    // Handle audio playback
    console.log(`Playing audio for card ${cardIndex} at ${timestamp}s`);
  };

  return (
    <div className="app">
      {bootstrapData && (
        <CurioCardStack
          bootstrapData={bootstrapData}
          onAudioPlay={handleAudioPlay}
        />
      )}
    </div>
  );
}
```

## Props

### `bootstrapData` (required)
Type: `BootstrapResponse`

The bootstrap API response containing:
- `news_items`: Array of news items
- `script`: Full script text
- `word_timings`: Word timing data for segmentation
- `agentOutputs`: Agent outputs (favorite story, media enhancements, etc.)
- `audio_url`: URL for audio narration

### `onAudioPlay` (optional)
Type: `(cardIndex: number, timestamp: number) => void`

Callback function called when the audio button is clicked on a card.
- `cardIndex`: Index of the current card
- `timestamp`: Audio timestamp in seconds for this card

## Card Types

The component automatically renders different card types:

1. **Overview Card** (type: 'overview')
   - First card in the sequence
   - Shows date, highlights, and story count
   - Sparkles icon and "Tap to begin" CTA

2. **Story Cards** (type: CategoryType)
   - Individual news stories
   - Background media (video/image/GIF)
   - Category tag, title, summary
   - Audio button and navigation dots

## Media Preloading

The component automatically preloads media for the next 2 cards to ensure smooth transitions:

```typescript
// Preloads cards at index: currentCardIndex + 1, currentCardIndex + 2
preloadNextMedia();
```

- Videos: Preloaded with `preload="auto"`
- Images: Preloaded using `new Image()`
- Tracked in `preloadedMedia` Map to avoid duplicate loads

## Keyboard Navigation

| Key | Action |
|-----|--------|
| `→` or `↓` | Next card |
| `←` or `↑` | Previous card |

## Responsive Design

### Mobile (< 768px)
- Full viewport dimensions (100vw × 100vh)
- Touch-optimized swipe gestures
- Full-screen immersive experience

### Desktop (≥ 768px)
- Fixed dimensions (380px × 680px)
- Centered on screen with black background
- Border radius and box shadow
- Mouse swipe support for testing

## Accessibility

- **ARIA Labels**: Proper labels for screen readers
- **Keyboard Navigation**: Full keyboard support
- **Progress Indicator**: Visual and ARIA progress bar
- **Reduced Motion**: Respects `prefers-reduced-motion`
- **High Contrast**: Supports `prefers-contrast: high`

## Performance

- **GPU Acceleration**: Uses `transform: translateZ(0)` for smooth animations
- **Lazy Loading**: Only renders current card (future: adjacent cards)
- **Media Preloading**: Preloads next 2 cards' media
- **Containment**: Uses CSS `contain` for optimized rendering

## Animation Details

```typescript
const cardVariants = {
  enter: {
    opacity: 0,
    y: 50,      // Start 50px below
    scale: 0.95 // Start slightly smaller
  },
  center: {
    opacity: 1,
    y: 0,       // Center position
    scale: 1,   // Full size
    transition: {
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1] // Custom cubic-bezier
    }
  },
  exit: {
    opacity: 0,
    y: -50,     // Exit 50px above
    scale: 0.95, // Exit slightly smaller
    transition: {
      duration: 0.3
    }
  }
};
```

## Requirements Satisfied

- **1.1**: Full-screen card interface (380px × 680px)
- **1.2**: Tap/click and navigation
- **1.3**: Navigation dots (implemented in StoryCard)
- **1.4**: Swipe gesture support
- **1.5**: Smooth animations (500ms)
- **5.1-5.4**: Framer Motion animations with custom easing
- **11.6**: Media preloading for next 2 cards

## Future Enhancements

- Virtual scrolling for large card sets
- Infinite scroll/loop mode
- Card bookmarking
- Share individual cards
- Analytics tracking for card views
- Auto-advance with audio sync
