import { useEffect, useRef } from 'react';
import { mediaPreloader, PreloadableMedia } from '../utils/mediaPreloader';

interface UseMediaPreloaderOptions {
  cards: PreloadableMedia[];
  currentIndex: number;
  enabled?: boolean;
}

/**
 * Hook to manage media preloading for card navigation
 */
export const useMediaPreloader = ({
  cards,
  currentIndex,
  enabled = true
}: UseMediaPreloaderOptions): void => {
  const cleanupIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!enabled || cards.length === 0) {
      return;
    }

    // Preload media for next cards
    mediaPreloader.preloadNextMedia(cards, currentIndex);

    // Setup periodic cleanup of expired media
    if (!cleanupIntervalRef.current) {
      cleanupIntervalRef.current = setInterval(() => {
        mediaPreloader.cleanupExpiredMedia();
      }, 30000); // Check every 30 seconds
    }

    // Cleanup on unmount
    return () => {
      if (cleanupIntervalRef.current) {
        clearInterval(cleanupIntervalRef.current);
        cleanupIntervalRef.current = null;
      }
    };
  }, [cards, currentIndex, enabled]);

  // Cleanup all media when component unmounts
  useEffect(() => {
    return () => {
      mediaPreloader.clearAll();
    };
  }, []);
};
