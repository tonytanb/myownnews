import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { OverviewCardProps } from './types';
import BackgroundMedia from './BackgroundMedia';
import './OverviewCard.css';

/**
 * OverviewCard Component
 * 
 * The first card shown to users, providing a summary of the day's content.
 * Features:
 * - Centered content with Sparkles icon
 * - Current date in long format
 * - 4-6 emoji-prefixed highlights from news items
 * - "Tap to begin →" instructional text
 * - Fade-in animation with 300ms delay
 * 
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 5.5
 */
const OverviewCard: React.FC<OverviewCardProps> = ({
  date,
  highlights,
  totalStories,
  backgroundImage,
  onTap
}) => {
  // Format date to long format (e.g., "Monday, November 16, 2025")
  const formatDate = (dateString: string): string => {
    const dateObj = new Date(dateString);
    return dateObj.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Animation variants for content appearance with 300ms delay
  const contentVariants = {
    hidden: { 
      opacity: 0 
    },
    visible: {
      opacity: 1,
      transition: {
        delay: 0.3,
        duration: 0.5,
        ease: [0.4, 0, 0.2, 1] as const
      }
    }
  } as const;

  return (
    <div 
      className="overview-card" 
      onClick={onTap}
      role="article"
      aria-label={`Overview card for ${formatDate(date)}. ${totalStories} stories available.`}
      aria-describedby="overview-content"
    >
      {/* Background media with gradient overlay */}
      <BackgroundMedia
        mediaUrl={backgroundImage}
        mediaType="image"
        alt="Curio overview background with gradient overlay"
        category="news"
      />

      {/* Centered content with fade-in animation */}
      <motion.div
        className="overview-card__content"
        initial="hidden"
        animate="visible"
        variants={contentVariants}
        id="overview-content"
      >
        {/* Sparkles icon */}
        <div className="overview-card__icon" aria-hidden="true">
          <Sparkles size={48} className="overview-card__sparkles" />
        </div>

        {/* Title */}
        <h1 className="overview-card__title" id="overview-title">
          Today in Curio 🪄
        </h1>

        {/* Date in long format */}
        <p className="overview-card__date" aria-label={`Date: ${formatDate(date)}`}>
          {formatDate(date)}
        </p>

        {/* Story count */}
        <p className="overview-card__story-count" role="status">
          {totalStories} {totalStories === 1 ? 'story' : 'stories'} curated for you
        </p>

        {/* Highlights with emoji prefixes */}
        <div 
          className="overview-card__highlights"
          role="list"
          aria-label="Story highlights"
        >
          {highlights.slice(0, 6).map((highlight, index) => (
            <div 
              key={index} 
              className="overview-card__highlight"
              role="listitem"
            >
              {highlight}
            </div>
          ))}
        </div>

        {/* Instructional text */}
        <div className="overview-card__cta" role="button" tabIndex={0}>
          <span className="overview-card__cta-text">Tap to begin</span>
          <span className="overview-card__cta-arrow" aria-hidden="true">→</span>
        </div>
      </motion.div>

      {/* Curio watermark */}
      <div className="overview-card__watermark" aria-hidden="true">
        curio
      </div>
    </div>
  );
};

export default OverviewCard;
