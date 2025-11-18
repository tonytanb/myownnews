# Implementation Plan

- [x] 1. Remove demo language and update to product messaging
  - Update "Agent-Powered News Demo" to "Listen to Today's Brief" in App.tsx
  - Remove demo description text from audio section
  - Update page title and subtitle to production language
  - Remove any "demo" references throughout the application
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Fix audio playback functionality
- [x] 2.1 Investigate and fix audio URL generation in backend
  - Check if Polly synthesis is being called in multi_agent_orchestrator.py
  - Verify audio URL is included in bootstrap response
  - Ensure audio files are being uploaded to S3
  - Add logging to track audio generation flow
  - _Requirements: 2.1, 2.2_

- [x] 2.2 Update AudioPlayer component to handle audio states
  - Add loading state while audio is being generated
  - Display error message if audio fails to load
  - Implement retry mechanism for failed audio
  - Add fallback to sample audio if generation fails
  - _Requirements: 2.2, 2.3, 2.5_

- [x] 2.3 Test audio playback end-to-end
  - Verify play button triggers audio playback
  - Confirm word highlighting syncs with audio
  - Test error handling for missing audio
  - _Requirements: 2.2, 2.4_

- [x] 3. Clean interactive transcript display
- [x] 3.1 Implement script cleaning function
  - Create cleanScript() function to remove stage directions
  - Filter out text within asterisks (*...*)
  - Remove prompt instructions and meta-text
  - Normalize whitespace and trim content
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3.2 Update InteractiveTranscript component
  - Apply cleanScript() to script prop before rendering
  - Add empty state message when no transcript available
  - Test with various script formats
  - _Requirements: 3.1, 3.5_

- [x] 4. Ensure all news items have images
- [x] 4.1 Add image fallback logic to backend
  - Update multi_agent_orchestrator.py to ensure all news items have images
  - Generate Unsplash fallback URLs for items without images
  - Use category and title keywords for relevant fallback images
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 4.2 Add frontend image fallback handling
  - Create getNewsImage() helper function in NewsItems.tsx
  - Implement fallback to Unsplash if image URL is missing
  - Add error handling for failed image loads
  - Display styled placeholder for completely failed images
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4.3 Verify all 7 news items display images
  - Test with various news data scenarios
  - Confirm fallback images are relevant to content
  - Check image loading performance
  - _Requirements: 4.4_

- [ ] 5. Create analytics screen and menu navigation
- [ ] 5.1 Create AnalyticsScreen component
  - Create new file curio-news-ui/src/components/AnalyticsScreen.tsx
  - Implement full-screen overlay layout
  - Add back button to return to main page
  - Include all analytics sections (provenance, collaboration, metrics, debugging)
  - _Requirements: 5.5, 5.6_

- [ ] 5.2 Add menu button and dropdown to header
  - Create Menu component with dropdown functionality
  - Add "Analytics" menu item
  - Add "About" menu item for future use
  - Style menu to match application design
  - _Requirements: 5.2, 5.3_

- [ ] 5.3 Implement analytics screen navigation
  - Add state management for showing/hiding analytics screen
  - Connect menu "Analytics" option to show analytics screen
  - Implement close functionality to return to main page
  - _Requirements: 5.3, 5.4, 5.6_

- [ ] 5.4 Remove analytics from main landing page
  - Remove provenance section from main App.tsx render
  - Remove "Show Analytics" toggle button
  - Hide agent collaboration trace from main page (keep for analytics screen)
  - Ensure main page focuses only on news content
  - _Requirements: 5.1, 5.7_

- [ ] 5.5 Style analytics screen
  - Create AnalyticsScreen.css with full-screen overlay styles
  - Ensure responsive design for mobile devices
  - Add smooth transitions for opening/closing
  - Match existing application color scheme
  - _Requirements: 5.5_

- [x] 6. Deploy and verify all changes
  - Build frontend with all updates
  - Deploy backend changes if audio fix requires it
  - Sync frontend to S3
  - Test all functionality in production
  - Verify no demo language remains
  - Confirm audio playback works
  - Check all images display
  - Test analytics screen navigation
  - _Requirements: All_
