import React, { useState, useEffect, useRef } from 'react';
import { 
  getOptimizedImageUrl, 
  getOptimizedVideoUrl, 
  getBestImageFormat,
  getResponsiveImageSrcSet 
} from '../../utils/mediaOptimizer';
import { performanceMonitor } from '../../utils/performanceMonitor';
import './BackgroundMedia.css';

interface BackgroundMediaProps {
  mediaUrl: string;
  mediaType: 'video' | 'image' | 'gif';
  fallbackImage?: string;
  alt: string;
  category?: string;
  cardIndex?: number;
  onError?: (errorType: 'video' | 'image' | 'unsplash' | 'placeholder') => void;
}

const BackgroundMedia: React.FC<BackgroundMediaProps> = ({
  mediaUrl,
  mediaType,
  fallbackImage,
  alt,
  category = 'news',
  cardIndex = 0,
  onError
}) => {
  const [currentMediaUrl, setCurrentMediaUrl] = useState(mediaUrl);
  const [currentMediaType, setCurrentMediaType] = useState(mediaType);
  const [hasError, setHasError] = useState(false);
  const [errorCount, setErrorCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const maxRetries = 3; // Maximum fallback attempts

  useEffect(() => {
    // Optimize media URL based on type (Subtask 13.2)
    // Requirements: 11.1, 11.2, 11.3
    let optimizedUrl = mediaUrl;
    
    if (mediaType === 'video') {
      // Optimize video: compress to < 5MB, limit resolution to 800x400
      optimizedUrl = getOptimizedVideoUrl(mediaUrl);
    } else {
      // Optimize image: use WebP format, limit resolution to 800x400
      const preferredFormat = getBestImageFormat();
      optimizedUrl = getOptimizedImageUrl(mediaUrl, { 
        preferredImageFormat: preferredFormat,
        maxImageWidth: 800,
        maxImageHeight: 400
      });
    }
    
    // Start tracking media load time (Subtask 13.3)
    // Requirements: 12.2
    performanceMonitor.startMediaLoad(optimizedUrl);
    
    setCurrentMediaUrl(optimizedUrl);
    setCurrentMediaType(mediaType);
    setHasError(false);
    setErrorCount(0);
    setIsLoading(true);
  }, [mediaUrl, mediaType]);

  const handleMediaLoad = () => {
    setIsLoading(false);
    
    // End tracking media load time (Subtask 13.3)
    // Requirements: 12.2
    performanceMonitor.endMediaLoad(currentMediaUrl, currentMediaType, cardIndex);
  };

  const generateUnsplashUrl = (category: string, seed: string): string => {
    // Create deterministic hash from seed for consistent images
    const hash = seed.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc);
    }, 0);
    
    const categoryKeywords: Record<string, string> = {
      favorite: 'featured,highlight',
      world: 'world,global,international',
      local: 'city,community,local',
      event: 'event,celebration,gathering',
      movie: 'cinema,film,movie',
      music: 'music,concert,performance',
      book: 'book,reading,literature',
      news: 'news,journalism,media'
    };

    const keywords = categoryKeywords[category] || 'news';
    const baseUrl = `https://source.unsplash.com/800x400/?${keywords}&sig=${Math.abs(hash)}`;
    
    // Optimize Unsplash URL (Subtask 13.2)
    // Requirements: 11.2, 11.3
    const preferredFormat = getBestImageFormat();
    return getOptimizedImageUrl(baseUrl, {
      preferredImageFormat: preferredFormat,
      maxImageWidth: 800,
      maxImageHeight: 400
    });
  };

  const generatePlaceholder = (category: string): string => {
    const categoryColors: Record<string, string> = {
      favorite: 'ec4899/f43f5e',
      world: '3b82f6/6366f1',
      local: '10b981/059669',
      event: 'f59e0b/d97706',
      movie: '8b5cf6/7c3aed',
      music: 'ef4444/dc2626',
      book: '06b6d4/0891b2',
      news: '6b7280/4b5563'
    };

    const colors = categoryColors[category] || '6b7280/4b5563';
    const emoji = {
      favorite: '⭐',
      world: '🌍',
      local: '📍',
      event: '🎉',
      movie: '🎬',
      music: '🎵',
      book: '📚',
      news: '📰'
    }[category] || '📰';

    return `https://via.placeholder.com/800x400/${colors}?text=${encodeURIComponent(emoji)}`;
  };

  const handleMediaError = () => {
    // Record media load failure (Subtask 13.3)
    // Requirements: 12.2
    performanceMonitor.recordMediaLoadFailure(currentMediaUrl, currentMediaType);
    
    // Prevent infinite error loops
    if (errorCount >= maxRetries) {
      console.error('BackgroundMedia: Max retries reached, using final placeholder');
      return;
    }

    setErrorCount(prev => prev + 1);
    setHasError(true);
    
    // Fallback cascade: video -> fallback image -> Unsplash -> placeholder
    
    // 1. If video failed, try fallback image
    if (currentMediaType === 'video' && fallbackImage && currentMediaUrl !== fallbackImage) {
      console.warn('BackgroundMedia: Video load failed, trying fallback image');
      setCurrentMediaUrl(fallbackImage);
      setCurrentMediaType('image');
      onError?.('video');
      return;
    }
    
    // 2. If original image or video fallback failed, try Unsplash
    if (!currentMediaUrl.includes('unsplash.com')) {
      console.warn('BackgroundMedia: Image load failed, trying Unsplash');
      const unsplashUrl = generateUnsplashUrl(category, alt);
      setCurrentMediaUrl(unsplashUrl);
      setCurrentMediaType('image');
      onError?.('image');
      return;
    }
    
    // 3. If Unsplash failed, use colored placeholder (final fallback)
    if (!currentMediaUrl.includes('placeholder.com')) {
      console.warn('BackgroundMedia: Unsplash failed, using placeholder');
      const placeholderUrl = generatePlaceholder(category);
      setCurrentMediaUrl(placeholderUrl);
      setCurrentMediaType('image');
      onError?.('unsplash');
      return;
    }
    
    // 4. If even placeholder fails (shouldn't happen), log error
    console.error('BackgroundMedia: All fallbacks exhausted');
    onError?.('placeholder');
  };

  const renderMedia = () => {
    if (currentMediaType === 'video') {
      return (
        <video
          ref={videoRef}
          className="background-media__video"
          src={currentMediaUrl}
          autoPlay
          muted
          loop
          playsInline
          onError={handleMediaError}
          onLoadedData={handleMediaLoad}
          onCanPlay={handleMediaLoad}
          aria-label={`Background video: ${alt}`}
          role="img"
        />
      );
    }

    // Both image and gif are rendered as img elements
    // Use responsive srcset for different pixel densities (Subtask 13.2)
    // Requirements: 11.2, 11.3
    const srcSet = getResponsiveImageSrcSet(currentMediaUrl, {
      preferredImageFormat: getBestImageFormat(),
      maxImageWidth: 800,
      maxImageHeight: 400
    });
    
    return (
      <img
        className="background-media__image"
        src={currentMediaUrl}
        srcSet={srcSet}
        sizes="(max-width: 768px) 100vw, 380px"
        alt={alt}
        onError={handleMediaError}
        onLoad={handleMediaLoad}
        role="img"
        loading="lazy"
        decoding="async"
      />
    );
  };

  return (
    <div className="background-media" role="presentation">
      {isLoading && (
        <div className="background-media__loading" aria-label="Loading media" role="status">
          <div className="background-media__spinner" aria-hidden="true" />
          <span className="sr-only">Loading background media</span>
        </div>
      )}
      {renderMedia()}
      <div className="background-media__overlay" aria-hidden="true" />
    </div>
  );
};

export default BackgroundMedia;
