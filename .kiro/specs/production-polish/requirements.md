# Production Polish Requirements

## Introduction

Transform Curio News from demo mode to a production-ready news application. Remove demo language, fix audio playback, clean up the transcript display, ensure all news items have images, and move analytics/performance data to a separate menu screen.

## Glossary

- **Curio News System**: The AI-powered news curation and delivery application
- **Audio Player**: Component that plays the generated news briefing audio
- **Interactive Transcript**: Component displaying the news script with word-level timing
- **News Card**: Visual card displaying a news story with image, title, and summary
- **Analytics Screen**: Separate view showing agent provenance, performance metrics, and debugging information
- **Main Landing Page**: Primary user-facing page showing news content

## Requirements

### Requirement 1: Remove Demo Language

**User Story:** As a user, I want to see Curio News as a professional product, not a demo, so that I trust the service and feel it's production-ready.

#### Acceptance Criteria

1. WHEN the Main Landing Page loads, THE Curio News System SHALL display "Your AI-Curated News" instead of "Agent-Powered News Demo"
2. WHEN the audio section is displayed, THE Curio News System SHALL remove the text "Click below to experience our AI-curated news briefing with full provenance tracking"
3. WHEN the audio section is displayed, THE Curio News System SHALL display "Listen to Today's Brief" as the section title
4. WHEN any user-facing text is displayed, THE Curio News System SHALL use product language instead of demo language
5. WHEN the page title is displayed, THE Curio News System SHALL show "Today's Brief" without "demo" references

### Requirement 2: Fix Audio Playback

**User Story:** As a user, I want to hear the news briefing audio, so that I can consume news while multitasking.

#### Acceptance Criteria

1. WHEN the Audio Player component loads, THE Curio News System SHALL fetch a valid audio URL from the backend
2. WHEN the play button is clicked, THE Audio Player SHALL play the audio file without errors
3. IF no audio URL is available, THEN THE Curio News System SHALL display "Generating audio..." with a loading indicator
4. WHEN audio is playing, THE Audio Player SHALL update the current time and highlight transcript words
5. WHEN audio generation fails, THE Curio News System SHALL display a clear error message with retry option

### Requirement 3: Clean Interactive Transcript Display

**User Story:** As a user, I want to see only the actual news script in the transcript, so that I can read the content without confusion.

#### Acceptance Criteria

1. WHEN the Interactive Transcript displays, THE Curio News System SHALL show only the actual news script text
2. WHEN the Interactive Transcript displays, THE Curio News System SHALL NOT show any prompt text or instructions within the transcript content
3. WHEN the script starts with prompt text like "*opens with an upbeat, conversational tone*", THE Curio News System SHALL remove this text before display
4. WHEN the script contains stage directions or meta-instructions, THE Curio News System SHALL filter them out
5. WHEN the transcript is empty, THE Curio News System SHALL display "Transcript will appear here once audio is generated"

### Requirement 4: Ensure All News Items Have Images

**User Story:** As a user, I want to see images for all news stories, so that the interface looks complete and professional.

#### Acceptance Criteria

1. WHEN News Cards are displayed, THE Curio News System SHALL provide an image for each news item
2. IF a news item lacks an image URL, THEN THE Curio News System SHALL generate a fallback image URL using Unsplash or similar service
3. WHEN generating fallback images, THE Curio News System SHALL use the news category and keywords from the title
4. WHEN all 7 news items are displayed, THE Curio News System SHALL show images for all 7 items
5. WHEN an image fails to load, THE Curio News System SHALL display a styled placeholder with the category icon

### Requirement 5: Move Analytics to Separate Menu Screen

**User Story:** As a user, I want the main page to focus on news content, so that I can quickly consume information without technical distractions.

#### Acceptance Criteria

1. WHEN the Main Landing Page loads, THE Curio News System SHALL NOT display agent provenance, performance metrics, or debugging information
2. WHEN the Main Landing Page loads, THE Curio News System SHALL display a menu button in the header
3. WHEN the menu button is clicked, THE Curio News System SHALL show a dropdown menu with "Analytics" option
4. WHEN "Analytics" is selected from the menu, THE Curio News System SHALL navigate to a separate analytics screen
5. WHEN the Analytics Screen is displayed, THE Curio News System SHALL show agent provenance, collaboration traces, performance metrics, and debugging dashboard
6. WHEN the Analytics Screen is displayed, THE Curio News System SHALL provide a "Back to News" button to return to the main page
7. WHEN the user is on the Main Landing Page, THE Curio News System SHALL hide the "Show Analytics" toggle button
