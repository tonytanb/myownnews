# Implementation Plan: Mobile Card UI Redesign

## Overview

This plan transforms Curio's UI into a mobile-first card-based experience with swipeable story cards, video backgrounds, and smooth animations. Each task builds incrementally toward the complete implementation.

---

## Tasks

- [x] 1. Install dependencies and set up project structure
  - Install framer-motion, lucide-react, and react-swipeable packages
  - Create new component directories: components/cards/, components/cards/types.ts
  - Set up TypeScript interfaces for card data structures
  - _Requirements: 1.1, 9.1_

- [x] 2. Implement core data transformation layer
  - [x] 2.1 Create script segmentation algorithm
    - Write function to split script into 15-30 second segments using word timings
    - Implement sentence boundary detection for natural breaks
    - Add duration calculation per segment
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [x] 2.2 Create agent output to card data transformer
    - Map Content Curator output to StoryCard structure
    - Transform Story Selector favorite story to first card
    - Integrate Media Enhancer output for background media
    - Map Entertainment Curator recommendations to weekend cards
    - _Requirements: 9.1, 9.2, 9.3, 9.5, 9.6_
  
  - [x] 2.3 Implement category mapping and configuration
    - Create category type definitions (favorite, world, local, event, movie, music, book)
    - Define gradient colors and icons for each category
    - Map news categories to card categories
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Build BackgroundMedia component
  - [x] 3.1 Create media rendering component
    - Implement video background with autoplay, muted, loop, playsInline
    - Implement image background with object-fit cover
    - Add brightness filter (50%) and gradient overlay
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 3.2 Implement media fallback system
    - Add error handling for failed video loads
    - Implement Unsplash API fallback with category keywords
    - Create placeholder generator with colored gradients
    - _Requirements: 4.5, 11.5_
  
  - [x] 3.3 Add media preloading logic
    - Preload media for next 2 cards
    - Implement preload queue management
    - Add memory cleanup for distant cards
    - _Requirements: 11.6_

- [x] 4. Create CategoryTag component
  - Implement gradient background with Tailwind classes
  - Add Lucide icon rendering (Heart, Globe, MapPin, Film, Music, Book)
  - Style with rounded corners, shadow, and white text
  - Position in top-left corner with proper spacing
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5. Build OverviewCard component
  - [x] 5.1 Create overview card layout
    - Add centered content with Sparkles icon
    - Display "Today in Curio 🪄" title
    - Show current date in long format
    - Add 4-6 emoji-prefixed highlights from news items
    - Include "Tap to begin →" instructional text
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 5.2 Add overview card animations
    - Implement fade-in animation with 300ms delay
    - Add Framer Motion variants for content appearance
    - _Requirements: 5.5_

- [x] 6. Build StoryCard component
  - [x] 6.1 Create story card layout structure
    - Implement full-screen card container (380px × 680px)
    - Add BackgroundMedia component integration
    - Position CategoryTag in top-left
    - Add Curio watermark in top-right
    - _Requirements: 1.1, 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 6.2 Implement story content area
    - Position title 24px from bottom
    - Style title with 2xl font, semibold weight
    - Add summary text with small font, gray-200 color
    - Ensure text readability with gradient overlay
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 6.3 Add audio controls
    - Create audio button with Volume2 icon
    - Style with frosted glass effect (white/20% background, backdrop blur)
    - Add hover state (white/30% background)
    - Position in bottom-left with "Tap to listen" helper text
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 6.4 Add navigation dots
    - Create dot indicators for all cards
    - Highlight current card dot
    - Position in bottom-right corner
    - _Requirements: 1.3_

- [x] 7. Implement CurioCardStack container
  - [x] 7.1 Create card stack state management
    - Initialize currentCardIndex state
    - Create cards array from transformed data
    - Manage isTransitioning state
    - Track preloaded media in Map
    - _Requirements: 1.1, 1.2_
  
  - [x] 7.2 Implement card navigation
    - Create nextCard() function with animation
    - Create previousCard() function
    - Add keyboard navigation (arrow keys)
    - Implement tap/click to advance
    - _Requirements: 1.2, 1.4_
  
  - [x] 7.3 Add Framer Motion animations
    - Configure enter/center/exit variants
    - Set 500ms transition duration
    - Add custom easing curve
    - Implement AnimatePresence for card transitions
    - _Requirements: 1.5, 5.1, 5.2, 5.3, 5.4_
  
  - [x] 7.4 Implement swipe gesture handling
    - Integrate react-swipeable library
    - Add onSwipeLeft → nextCard()
    - Add onSwipeRight → previousCard()
    - Configure swipe threshold (50px) and velocity
    - _Requirements: 1.4_

- [x] 8. Integrate audio playback with cards
  - [x] 8.1 Create audio state management
    - Track current playing card index
    - Manage global audio element
    - Sync audio currentTime with card timestamps
    - _Requirements: 7.1, 10.4_
  
  - [x] 8.2 Implement per-card audio playback
    - Seek to card's audio timestamp on play
    - Auto-advance to next card when segment ends
    - Pause audio on manual card navigation
    - _Requirements: 10.1, 10.2_

- [x] 9. Add responsive design and styling
  - [x] 9.1 Implement mobile-first CSS
    - Set card to full viewport on mobile (100vw × 100vh)
    - Add touch-friendly button sizes (44px × 44px minimum)
    - Optimize text sizes for mobile readability
    - _Requirements: 13.3, 13.5_
  
  - [x] 9.2 Add desktop adaptation
    - Center card on desktop (380px × 680px)
    - Add black background outside card area
    - Add border-radius and box-shadow to card
    - _Requirements: 13.1, 13.2, 13.4_

- [x] 10. Implement error handling and fallbacks
  - [x] 10.1 Add media loading error handlers
    - Catch video load failures
    - Fallback to static image
    - Fallback to Unsplash if image fails
    - Ultimate fallback to colored placeholder
    - _Requirements: 11.5_
  
  - [x] 10.2 Add script segmentation fallbacks
    - Handle missing word timings
    - Generate segments from news summaries
    - Use default 20-second duration per card
    - _Requirements: 10.5_

- [x] 11. Integrate with existing App.tsx
  - [x] 11.1 Add feature flag for card UI
    - Create ENABLE_CARD_UI environment variable
    - Conditionally render CurioCardStack or existing UI
    - Preserve existing components for rollback
    - _Requirements: 9.7_
  
  - [x] 11.2 Transform bootstrap data to cards
    - Call transformToCards() on bootstrap response
    - Pass transformed data to CurioCardStack
    - Maintain compatibility with existing API
    - _Requirements: 9.1, 9.7_
  
  - [x] 11.3 Preserve agent trace and analytics
    - Keep AgentTrace component accessible
    - Maintain orchestration trace display
    - Add analytics overlay for card UI
    - _Requirements: 9.7_

- [x] 12. Add accessibility features
  - [x] 12.1 Implement keyboard navigation
    - Arrow keys for card navigation
    - Space/Enter for audio playback
    - Escape for closing modals
    - _Requirements: 13.5_
  
  - [x] 12.2 Add ARIA labels and screen reader support
    - Label all interactive elements
    - Announce card transitions
    - Describe media content
    - Add alt text for images
    - _Requirements: 13.5_
  
  - [x] 12.3 Ensure contrast ratios
    - Verify text contrast meets WCAG 2.1 AA (4.5:1)
    - Test gradient overlays for readability
    - Validate category tag contrast
    - _Requirements: 8.4_

- [x] 13. Performance optimization
  - [x] 13.1 Implement lazy loading
    - Only render current card + adjacent cards
    - Unload cards > 3 positions away
    - Use React.lazy for card components
    - _Requirements: 11.6_
  
  - [x] 13.2 Optimize media assets
    - Compress videos to < 5MB
    - Use WebP format for images
    - Limit resolution to 800x400
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [x] 13.3 Add performance monitoring
    - Track card transition times
    - Monitor memory usage
    - Log media load times
    - _Requirements: 12.1, 12.2_

- [x] 14. Testing and validation
  - [x] 14.1 Test card navigation flow
    - Verify swipe gestures work on mobile
    - Test keyboard navigation on desktop
    - Validate tap-to-advance functionality
    - _Requirements: 1.2, 1.4_
  
  - [x] 14.2 Test media loading and fallbacks
    - Simulate video load failures
    - Verify Unsplash fallback works
    - Test placeholder generation
    - _Requirements: 4.5, 11.5_
  
  - [x] 14.3 Test audio synchronization
    - Verify audio plays from correct timestamp
    - Test auto-advance on segment end
    - Validate pause on manual navigation
    - _Requirements: 10.1, 10.2_
  
  - [x] 14.4 Test responsive design
    - Verify mobile layout (380px width)
    - Test desktop centered layout
    - Validate touch targets (44px minimum)
    - _Requirements: 13.1, 13.2, 13.3, 13.5_

- [x] 15. Deploy and monitor
  - Build production bundle with feature flag enabled
  - Deploy to staging environment for testing
  - Monitor performance metrics (load time, transitions)
  - Gather user feedback and iterate
  - _Requirements: All_
