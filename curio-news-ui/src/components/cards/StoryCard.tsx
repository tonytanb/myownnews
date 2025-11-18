/**
 * StoryCard Component
 * Full-screen swipeable card displaying a single news story with media background
 * Requirements: 1.1, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5
 */

import React from 'react';
import { Volume2 } from 'lucide-react';
import { StoryCardProps } from './types';
import BackgroundMedia from './BackgroundMedia';
import CategoryTag from './CategoryTag';
import './StoryCard.css';

/**
 * StoryCard component
 * Renders a full-screen card with background media, category tag, story content, and audio controls
 * 
 * @param story - News item data
 * @param categoryType - Category for visual styling
 * @param scriptSegment - Text content for this card
 * @param estimatedDuration - Duration in seconds
 * @param mediaUrl - URL for background media
 * @param mediaType - Type of media (video/image/gif)
 * @param onAudioPlay - Callback when audio button is clicked
 * @param onTap - Callback when card is tapped
 * @param currentCardIndex - Current card position (for navigation dots)
 * @param totalCards - Total number of cards (for navigation dots)
 * @param isAudioPlaying - Whether audio is currently playing for this card
 */
export const StoryCard: React.FC<StoryCardProps & { 
  currentCardIndex?: number; 
  totalCards?: number;
  isAudioPlaying?: boolean;
}> = ({
  story,
  categoryType,
  scriptSegment,
  estimatedDuration,
  mediaUrl,
  mediaType,
  onAudioPlay,
  onTap,
  currentCardIndex = 0,
  totalCards = 1,
  isAudioPlaying = false
}) => {
  return (
    <div 
      className="story-card"
      onClick={onTap}
      role="article"
      aria-label={`Story: ${story.title}. From ${story.source}. ${categoryType} category.`}
      aria-describedby={`story-content-${currentCardIndex}`}
    >
      {/* Background Media */}
      <BackgroundMedia
        mediaUrl={mediaUrl}
        mediaType={mediaType}
        fallbackImage={story.image_url || ''}
        alt={`Background image for ${story.title}`}
        category={categoryType}
      />

      {/* Category Tag - Top Left */}
      <CategoryTag category={categoryType} />

      {/* Curio Watermark - Top Right */}
      <div className="story-card__watermark" aria-hidden="true">
        curio
      </div>

      {/* Story Content Area - Bottom */}
      <div className="story-card__content" id={`story-content-${currentCardIndex}`}>
        <h2 className="story-card__title" id={`story-title-${currentCardIndex}`}>
          {story.title}
        </h2>
        <p className="story-card__summary" id={`story-summary-${currentCardIndex}`}>
          {story.summary}
        </p>
      </div>

      {/* Audio Controls - Bottom Left */}
      <button
        className={`story-card__audio-button ${isAudioPlaying ? 'story-card__audio-button--playing' : ''}`}
        onClick={(e) => {
          e.stopPropagation();
          onAudioPlay();
        }}
        aria-label={isAudioPlaying 
          ? `Pause audio narration for ${story.title}. Estimated duration ${estimatedDuration} seconds.` 
          : `Play audio narration for ${story.title}. Estimated duration ${estimatedDuration} seconds.`
        }
        aria-pressed={isAudioPlaying}
        aria-describedby={`story-title-${currentCardIndex}`}
        type="button"
      >
        <Volume2 size={20} strokeWidth={2} aria-hidden="true" />
        <span className="story-card__audio-text" aria-hidden="true">
          {isAudioPlaying ? 'Playing...' : 'Tap to listen'}
        </span>
      </button>

      {/* Navigation Dots - Bottom Right */}
      <nav 
        className="story-card__navigation-dots" 
        aria-label="Card navigation"
        role="navigation"
      >
        {Array.from({ length: totalCards }).map((_, index) => (
          <div
            key={index}
            className={`story-card__dot ${
              index === currentCardIndex ? 'story-card__dot--active' : ''
            }`}
            role="img"
            aria-label={index === currentCardIndex 
              ? `Current card: ${index + 1} of ${totalCards}` 
              : `Card ${index + 1} of ${totalCards}`
            }
            aria-current={index === currentCardIndex ? 'true' : 'false'}
          />
        ))}
      </nav>
    </div>
  );
};

export default StoryCard;
