# StoryCard Component

## Overview

The `StoryCard` component is a full-screen, swipeable card that displays a single news story with rich media backgrounds, category indicators, and audio controls. It's designed for mobile-first consumption with smooth animations and intuitive interactions.

## Features

### 1. Layout Structure (Subtask 6.1)
- **Full-screen container**: 380px × 680px on desktop, 100vw × 100vh on mobile
- **BackgroundMedia integration**: Video, image, or GIF backgrounds with fallback system
- **CategoryTag positioning**: Top-left corner with gradient and icon
- **Curio watermark**: Top-right corner with subtle opacity

### 2. Story Content Area (Subtask 6.2)
- **Title**: 2xl font, semibold weight, positioned 24px from bottom
- **Summary**: Small font, gray-200 color, limited to 3 lines
- **Text readability**: Gradient overlay and text shadows ensure 4.5:1 contrast ratio
- **Responsive spacing**: Adjusts for mobile screens

### 3. Audio Controls (Subtask 6.3)
- **Frosted glass button**: White/20% background with backdrop blur
- **Volume2 icon**: From Lucide React
- **Hover state**: Increases to white/30% background
- **Helper text**: "Tap to listen" for user guidance
- **Positioned**: Bottom-left corner with proper spacing

### 4. Navigation Dots (Subtask 6.4)
- **Dot indicators**: Show total number of cards
- **Active state**: Current card highlighted with elongated dot
- **Positioned**: Bottom-right corner
- **Accessibility**: ARIA labels for screen readers

## Usage

```tsx
import { StoryCard } from './components/cards';

<StoryCard
  story={newsItem}
  categoryType="world"
  scriptSegment="This is the story script..."
  estimatedDuration={25}
  mediaUrl="https://example.com/video.mp4"
  mediaType="video"
  onAudioPlay={() => handleAudioPlay()}
  onTap={() => handleCardTap()}
  currentCardIndex={0}
  totalCards={5}
/>
```

## Props

| Prop | Type | Description |
|------|------|-------------|
| `story` | `NewsItem` | News item data with title, summary, source |
| `categoryType` | `CategoryType` | Category for visual styling (world, local, etc.) |
| `scriptSegment` | `string` | Text content for this card |
| `estimatedDuration` | `number` | Duration in seconds |
| `mediaUrl` | `string` | URL for background media |
| `mediaType` | `MediaType` | Type of media (video/image/gif) |
| `onAudioPlay` | `() => void` | Callback when audio button is clicked |
| `onTap` | `() => void` | Callback when card is tapped |
| `currentCardIndex` | `number` | Current card position (optional) |
| `totalCards` | `number` | Total number of cards (optional) |

## Accessibility

- **ARIA labels**: All interactive elements have descriptive labels
- **Keyboard navigation**: Audio button is keyboard accessible
- **Touch targets**: Minimum 44px × 44px for mobile
- **Contrast ratios**: Text meets WCAG 2.1 AA standards (4.5:1)
- **Screen reader support**: Card announces as article with story title

## Responsive Design

### Mobile (< 768px)
- Full viewport dimensions (100vw × 100vh)
- Optimized touch targets
- Adjusted font sizes and spacing

### Desktop (≥ 768px)
- Fixed dimensions (380px × 680px)
- Centered with border radius
- Box shadow for depth

## Styling

The component uses CSS modules with the following key classes:

- `.story-card`: Main container
- `.story-card__watermark`: Curio branding
- `.story-card__content`: Story text area
- `.story-card__title`: Story headline
- `.story-card__summary`: Story description
- `.story-card__audio-button`: Audio control button
- `.story-card__navigation-dots`: Dot indicators
- `.story-card__dot`: Individual dot
- `.story-card__dot--active`: Active dot state

## Requirements Met

- ✅ 1.1: Full-screen card interface (380px × 680px)
- ✅ 6.1: BackgroundMedia component integration
- ✅ 6.2: CategoryTag in top-left
- ✅ 6.3: Curio watermark in top-right
- ✅ 6.4: Non-selectable watermark
- ✅ 6.5: Proper z-index stacking
- ✅ 7.1: Audio button with Volume2 icon
- ✅ 7.2: Frosted glass effect
- ✅ 7.3: Hover state
- ✅ 7.4: Bottom-left positioning
- ✅ 7.5: Helper text
- ✅ 8.1: Title 24px from bottom
- ✅ 8.2: 2xl font, semibold weight
- ✅ 8.3: Summary with small font, gray-200
- ✅ 8.4: Text readability with gradient overlay
- ✅ 8.5: Proper text positioning
- ✅ 1.3: Navigation dots with active state

## Testing

The component includes comprehensive tests covering:

- ✅ Rendering all elements
- ✅ Navigation dots display
- ✅ Card tap interaction
- ✅ Audio button interaction
- ✅ Event propagation prevention
- ✅ Different category types
- ✅ Accessibility attributes
- ✅ Active dot highlighting

Run tests with:
```bash
npm test -- --testPathPattern=StoryCard.test.tsx
```

## Next Steps

This component is ready to be integrated into the `CurioCardStack` container (Task 7) which will handle:
- Card state management
- Navigation between cards
- Swipe gesture handling
- Framer Motion animations
- Audio synchronization
