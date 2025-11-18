interface PreloadableMedia {
  mediaUrl: string;
  mediaType: 'video' | 'image' | 'gif';
}

interface PreloadedMediaItem {
  element: HTMLVideoElement | HTMLImageElement;
  url: string;
  timestamp: number;
}

class MediaPreloader {
  private preloadQueue: Map<string, PreloadedMediaItem> = new Map();
  private readonly MAX_PRELOAD_DISTANCE = 2;
  private readonly MAX_CACHE_SIZE = 5;
  private readonly CACHE_TIMEOUT = 60000; // 1 minute

  /**
   * Preload media for upcoming cards
   * @param cards Array of cards with media information
   * @param currentIndex Current card index
   */
  preloadNextMedia(cards: PreloadableMedia[], currentIndex: number): void {
    // Preload next 2 cards
    for (let i = 1; i <= this.MAX_PRELOAD_DISTANCE; i++) {
      const nextIndex = currentIndex + i;
      if (nextIndex < cards.length) {
        const card = cards[nextIndex];
        this.preloadMedia(card.mediaUrl, card.mediaType);
      }
    }

    // Cleanup distant cards
    this.cleanupDistantMedia(cards, currentIndex);
  }

  /**
   * Preload a single media item
   * @param url Media URL
   * @param type Media type
   */
  private preloadMedia(url: string, type: 'video' | 'image' | 'gif'): void {
    // Skip if already preloaded
    if (this.preloadQueue.has(url)) {
      return;
    }

    // Check cache size limit
    if (this.preloadQueue.size >= this.MAX_CACHE_SIZE) {
      this.cleanupOldestMedia();
    }

    try {
      if (type === 'video') {
        const video = document.createElement('video');
        video.src = url;
        video.preload = 'auto';
        video.muted = true;
        video.load();

        this.preloadQueue.set(url, {
          element: video,
          url,
          timestamp: Date.now()
        });
      } else {
        // Both image and gif are preloaded as images
        const img = new Image();
        img.src = url;

        this.preloadQueue.set(url, {
          element: img,
          url,
          timestamp: Date.now()
        });
      }
    } catch (error) {
      console.warn(`Failed to preload media: ${url}`, error);
    }
  }

  /**
   * Cleanup media that is too far from current position
   * @param cards Array of cards
   * @param currentIndex Current card index
   */
  private cleanupDistantMedia(cards: PreloadableMedia[], currentIndex: number): void {
    const urlsToKeep = new Set<string>();

    // Keep current card and next 2 cards
    for (let i = currentIndex; i <= currentIndex + this.MAX_PRELOAD_DISTANCE && i < cards.length; i++) {
      urlsToKeep.add(cards[i].mediaUrl);
    }

    // Remove media not in the keep set
    const entries = Array.from(this.preloadQueue.entries());
    for (const [url, item] of entries) {
      if (!urlsToKeep.has(url)) {
        this.removeMedia(url, item);
      }
    }
  }

  /**
   * Remove oldest media from cache
   */
  private cleanupOldestMedia(): void {
    let oldestUrl: string | null = null;
    let oldestTimestamp = Date.now();

    const entries = Array.from(this.preloadQueue.entries());
    for (const [url, item] of entries) {
      if (item.timestamp < oldestTimestamp) {
        oldestTimestamp = item.timestamp;
        oldestUrl = url;
      }
    }

    if (oldestUrl) {
      const item = this.preloadQueue.get(oldestUrl);
      if (item) {
        this.removeMedia(oldestUrl, item);
      }
    }
  }

  /**
   * Remove media from cache and cleanup resources
   * @param url Media URL
   * @param item Preloaded media item
   */
  private removeMedia(url: string, item: PreloadedMediaItem): void {
    try {
      // Cleanup video resources
      if (item.element instanceof HTMLVideoElement) {
        item.element.pause();
        item.element.src = '';
        item.element.load();
      }
      
      // Remove from queue
      this.preloadQueue.delete(url);
    } catch (error) {
      console.warn(`Failed to cleanup media: ${url}`, error);
    }
  }

  /**
   * Cleanup expired media based on timeout
   */
  cleanupExpiredMedia(): void {
    const now = Date.now();
    const expiredUrls: string[] = [];

    const entries = Array.from(this.preloadQueue.entries());
    for (const [url, item] of entries) {
      if (now - item.timestamp > this.CACHE_TIMEOUT) {
        expiredUrls.push(url);
      }
    }

    expiredUrls.forEach(url => {
      const item = this.preloadQueue.get(url);
      if (item) {
        this.removeMedia(url, item);
      }
    });
  }

  /**
   * Clear all preloaded media
   */
  clearAll(): void {
    const entries = Array.from(this.preloadQueue.entries());
    for (const [url, item] of entries) {
      this.removeMedia(url, item);
    }
    this.preloadQueue.clear();
  }

  /**
   * Get preload queue size
   */
  getQueueSize(): number {
    return this.preloadQueue.size;
  }

  /**
   * Check if media is preloaded
   */
  isPreloaded(url: string): boolean {
    return this.preloadQueue.has(url);
  }
}

// Export singleton instance
export const mediaPreloader = new MediaPreloader();

// Export type for use in components
export type { PreloadableMedia };
