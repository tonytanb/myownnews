# Requirements Document

## Introduction

Transform Curio's UI from a traditional scrollable news feed into a modern, mobile-first card-based experience inspired by social media story formats. The new interface will feature full-screen swipeable cards with video backgrounds, smooth animations, and an immersive visual design that appeals to Gen Z users.

## Glossary

- **Curio System**: The news aggregation and personalization application
- **Story Card**: A full-screen card displaying a single news item or overview
- **Overview Card**: The first card shown to users, summarizing the day's content
- **Category Tag**: A visual badge indicating the content type (favorite, world, local, event, movie, music, book)
- **Framer Motion**: Animation library for React components
- **Lucide Icons**: Icon library for UI elements
- **Video Background**: Looping video content displayed behind card text

## Requirements

### Requirement 1

**User Story:** As a Gen Z user, I want to see news in a mobile-first card format, so that I can quickly swipe through stories like social media content

#### Acceptance Criteria

1. WHEN the Curio System loads, THE Curio System SHALL display a full-screen card interface optimized for mobile dimensions (380px × 680px)
2. WHEN a user taps or clicks a card, THE Curio System SHALL transition to the next story card with smooth animation
3. THE Curio System SHALL display navigation dots at the bottom of each card indicating the current position in the story sequence
4. THE Curio System SHALL support both tap/click and swipe gestures for card navigation
5. WHEN transitioning between cards, THE Curio System SHALL animate with fade and slide effects lasting 500 milliseconds

### Requirement 2

**User Story:** As a user, I want to see an overview card first, so that I can understand what stories are available today

#### Acceptance Criteria

1. WHEN the Curio System initializes, THE Curio System SHALL display an overview card as the first card in the sequence
2. THE overview card SHALL display the current date in long format (weekday, month, day, year)
3. THE overview card SHALL include a summary of available story categories with emoji indicators
4. THE overview card SHALL display a Sparkles icon and "Today in Curio 🪄" title
5. THE overview card SHALL include instructional text "Tap to begin →" to guide user interaction

### Requirement 3

**User Story:** As a user, I want each story card to have visual category indicators, so that I can quickly identify the type of content

#### Acceptance Criteria

1. WHEN displaying a story card, THE Curio System SHALL show a category tag in the top-left corner
2. THE category tag SHALL use gradient colors specific to each category type (pink-rose for favorite, blue-indigo for world, green-emerald for local, etc.)
3. THE category tag SHALL display an appropriate icon from Lucide Icons (Heart, Globe, MapPin, Film, Music, Book)
4. THE category tag SHALL include uppercase text label matching the category name
5. THE category tag SHALL have rounded corners, shadow effects, and white text for readability

### Requirement 4

**User Story:** As a user, I want story cards to have rich visual backgrounds, so that the content is more engaging and immersive

#### Acceptance Criteria

1. WHEN displaying a story card, THE Curio System SHALL show either a video background or static image background
2. WHERE a video background is available, THE Curio System SHALL autoplay the video in a muted loop
3. THE Curio System SHALL apply a brightness filter (50%) and gradient overlay to ensure text readability
4. THE gradient overlay SHALL transition from black/70% opacity at bottom to transparent at top
5. IF a video fails to load, THEN THE Curio System SHALL fallback to displaying the static image background

### Requirement 5

**User Story:** As a user, I want smooth animations when cards appear, so that the experience feels polished and modern

#### Acceptance Criteria

1. WHEN a new card enters the viewport, THE Curio System SHALL animate from opacity 0 to 1 and translate from Y position 50 to 0
2. WHEN a card exits the viewport, THE Curio System SHALL animate from opacity 1 to 0 and translate from Y position 0 to -50
3. THE Curio System SHALL use Framer Motion library for all card transition animations
4. THE animation duration SHALL be 500 milliseconds with smooth easing
5. WHEN the overview card content appears, THE Curio System SHALL delay the fade-in animation by 300 milliseconds

### Requirement 6

**User Story:** As a user, I want to see the Curio branding subtly displayed, so that I know which app I'm using without visual clutter

#### Acceptance Criteria

1. THE Curio System SHALL display a "curio" watermark logo in the top-right corner of each card
2. THE watermark SHALL use white text with 60% opacity
3. THE watermark SHALL use small font size (text-sm) with light weight and italic styling
4. THE watermark SHALL be positioned 16 pixels from the top and right edges
5. THE watermark SHALL be non-selectable (select-none CSS property)

### Requirement 7

**User Story:** As a user, I want to access audio narration for each story, so that I can listen while multitasking

#### Acceptance Criteria

1. WHEN displaying a story card (not overview), THE Curio System SHALL show an audio button in the bottom-left corner
2. THE audio button SHALL display a Volume2 icon from Lucide Icons
3. THE audio button SHALL have a frosted glass effect (white/20% background with backdrop blur)
4. WHEN hovering over the audio button, THE Curio System SHALL increase the background opacity to white/30%
5. THE audio button SHALL be accompanied by helper text "Tap to listen" in small gray text

### Requirement 8

**User Story:** As a user, I want story content to be clearly readable over backgrounds, so that I can easily consume the information

#### Acceptance Criteria

1. THE Curio System SHALL position story titles 24 pixels from the bottom of the card
2. THE story title SHALL use 2xl font size (text-2xl) with semibold weight and tight leading
3. THE story summary SHALL use small font size (text-sm) with gray-200 color and snug leading
4. THE Curio System SHALL apply text shadows or gradient overlays to ensure minimum contrast ratio of 4.5:1
5. THE Curio System SHALL position all text content above the audio controls and navigation dots

### Requirement 9

**User Story:** As a developer, I want to integrate this UI with existing Bedrock agent outputs, so that real curated news content populates the cards

#### Acceptance Criteria

1. THE Curio System SHALL map news items from Content Curator agent to the card format structure
2. THE Curio System SHALL use Social Impact Analyzer agent output to categorize stories by social relevance
3. THE Curio System SHALL display the Story Selector agent's favorite story as the first content card after overview
4. THE Curio System SHALL use Script Writer agent output to determine optimal story length and narrative flow
5. THE Curio System SHALL integrate Media Enhancer agent output to populate video/image backgrounds for each card
6. THE Curio System SHALL use Entertainment Curator agent recommendations for weekend entertainment cards
7. THE Curio System SHALL maintain compatibility with existing Bedrock orchestrator API endpoints

### Requirement 10

**User Story:** As a user, I want each story card to have the right length script, so that I can consume the content in bite-sized pieces

#### Acceptance Criteria

1. WHEN displaying a story card, THE Curio System SHALL show a script segment of 15-30 seconds duration
2. THE Curio System SHALL use Script Writer agent's word timing data to calculate per-card script length
3. THE Curio System SHALL split longer scripts into multiple cards when duration exceeds 30 seconds
4. THE Curio System SHALL display estimated read time or audio duration on each card
5. THE Curio System SHALL ensure each card's script is self-contained and coherent

### Requirement 11

**User Story:** As a user, I want rich media (images, GIFs, videos) for each story, so that the content is visually engaging

#### Acceptance Criteria

1. THE Curio System SHALL use Media Enhancer agent output to fetch optimized media for each story
2. WHERE video content is available from Media Enhancer, THE Curio System SHALL display looping video backgrounds
3. WHERE only images are available, THE Curio System SHALL display high-quality static images with parallax effects
4. IF Media Enhancer provides GIF content, THEN THE Curio System SHALL display animated GIFs as card backgrounds
5. THE Curio System SHALL fallback to Unsplash API for category-appropriate images when agent media is unavailable
6. THE Curio System SHALL preload media for the next 2 cards to ensure smooth transitions

### Requirement 12

**User Story:** As a developer, I want to understand current news API limitations, so that I can optimize content fetching

#### Acceptance Criteria

1. THE Curio System SHALL document current NewsAPI rate limits (100 requests per day on free tier)
2. THE Curio System SHALL use RSS feeds (Science Daily, NASA, Phys.org) as primary sources to avoid API limits
3. THE Curio System SHALL leverage Bedrock agents' web search capabilities to fetch real-time news without API constraints
4. THE Curio System SHALL cache news content in DynamoDB for 6 hours to minimize API calls
5. THE Curio System SHALL implement exponential backoff when API rate limits are reached

### Requirement 13

**User Story:** As a user, I want the interface to be responsive, so that it works well on different screen sizes

#### Acceptance Criteria

1. THE Curio System SHALL center the card interface on screens larger than mobile dimensions
2. THE Curio System SHALL maintain the 380px × 680px card dimensions on desktop displays
3. THE Curio System SHALL scale the card to full viewport dimensions on mobile devices
4. THE Curio System SHALL use a black background outside the card area on larger screens
5. THE Curio System SHALL ensure all touch targets meet minimum size requirements (44px × 44px) for accessibility
