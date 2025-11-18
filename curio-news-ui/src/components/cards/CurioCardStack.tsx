/**
 * CurioCardStack Component
 * Main container managing card state, navigation, and transitions
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.1, 5.2, 5.3, 5.4, 7.1, 10.4, 11.6
 */

import React, { useState, useEffect, useCallback, useRef, lazy, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSwipeable } from 'react-swipeable';
import { StoryCard as StoryCardType, BootstrapResponse, AudioState } from './types';
import { transformToCards } from '../../utils/cardTransformer';
import { performanceMonitor } from '../../utils/performanceMonitor';
import './CurioCardStack.css';

// Lazy load card components for better performance (Subtask 13.1)
// Requirements: 11.6
const OverviewCard = lazy(() => import('./OverviewCard'));
const StoryCard = lazy(() => import('./StoryCard'));

/**
 * Props for CurioCardStack component
 */
interface CurioCardStackProps {
  bootstrapData: BootstrapResponse;
  audioUrl?: string;
}

/**
 * Framer Motion animation variants for card transitions
 * Requirements: 1.5, 5.1, 5.2, 5.3, 5.4
 */
const cardVariants = {
  enter: {
    opacity: 0,
    y: 50,
    scale: 0.95
  },
  center: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1] as const // Custom easing curve
    }
  },
  exit: {
    opacity: 0,
    y: -50,
    scale: 0.95,
    transition: {
      duration: 0.3
    }
  }
} as const;

/**
 * CurioCardStack Component
 * 
 * Main container that manages:
 * - Card state and navigation
 * - Framer Motion animations
 * - Swipe gesture handling
 * - Media preloading
 * - Keyboard navigation
 * - Audio playback synchronization
 */
const CurioCardStack: React.FC<CurioCardStackProps> = ({
  bootstrapData,
  audioUrl
}) => {
  // ===== STATE MANAGEMENT (Subtask 7.1) =====
  
  // Current card index
  const [currentCardIndex, setCurrentCardIndex] = useState<number>(0);
  
  // Cards array from transformed data
  const [cards, setCards] = useState<StoryCardType[]>([]);
  
  // Transition state to prevent rapid navigation
  const [isTransitioning, setIsTransitioning] = useState<boolean>(false);
  
  // Preloaded media tracking
  const [preloadedMedia] = useState<Map<number, HTMLVideoElement | HTMLImageElement>>(
    new Map()
  );

  // ===== LAZY LOADING STATE (Subtask 13.1) =====
  // Requirements: 11.6
  
  // Track which cards should be rendered (current + adjacent cards)
  const [renderedCardIndices, setRenderedCardIndices] = useState<Set<number>>(new Set([0]));
  
  // Maximum distance from current card to keep rendered
  const RENDER_DISTANCE = 1; // Render current card + 1 adjacent on each side
  const UNLOAD_DISTANCE = 3; // Unload cards > 3 positions away

  // ===== PERFORMANCE MONITORING STATE (Subtask 13.3) =====
  // Requirements: 12.1, 12.2
  
  // Track performance metrics
  const [showPerformanceOverlay, setShowPerformanceOverlay] = useState<boolean>(false);
  
  // Performance monitoring ref
  const performanceMonitorRef = useRef(performanceMonitor);

  // ===== AUDIO STATE MANAGEMENT (Subtask 8.1) =====
  // Requirements: 7.1, 10.4
  
  // Audio element ref for global audio control
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  // Audio state tracking
  const [audioState, setAudioState] = useState<AudioState>({
    isPlaying: false,
    currentCardIndex: -1, // -1 means no card is playing
    audioElement: null,
    currentTime: 0
  });
  
  // Interval ref for checking audio segment end
  const audioCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize cards from bootstrap data
  useEffect(() => {
    const transformedCards = transformToCards(bootstrapData);
    setCards(transformedCards);
  }, [bootstrapData]);

  // ===== LAZY LOADING LOGIC (Subtask 13.1) =====
  // Requirements: 11.6
  
  /**
   * Update rendered card indices based on current position
   * Only render current card + adjacent cards within RENDER_DISTANCE
   * Unload cards > UNLOAD_DISTANCE positions away
   */
  useEffect(() => {
    if (cards.length === 0) return;

    const newRenderedIndices = new Set<number>();
    
    // Add current card
    newRenderedIndices.add(currentCardIndex);
    
    // Add adjacent cards within RENDER_DISTANCE
    for (let i = 1; i <= RENDER_DISTANCE; i++) {
      // Previous cards
      if (currentCardIndex - i >= 0) {
        newRenderedIndices.add(currentCardIndex - i);
      }
      // Next cards
      if (currentCardIndex + i < cards.length) {
        newRenderedIndices.add(currentCardIndex + i);
      }
    }
    
    // Remove cards beyond UNLOAD_DISTANCE
    const indicesToRemove: number[] = [];
    renderedCardIndices.forEach(index => {
      const distance = Math.abs(index - currentCardIndex);
      if (distance > UNLOAD_DISTANCE) {
        indicesToRemove.push(index);
        
        // Cleanup preloaded media for unloaded cards
        if (preloadedMedia.has(index)) {
          const media = preloadedMedia.get(index);
          if (media instanceof HTMLVideoElement) {
            media.pause();
            media.src = '';
            media.load();
          }
          preloadedMedia.delete(index);
        }
      }
    });
    
    setRenderedCardIndices(newRenderedIndices);
  }, [currentCardIndex, cards.length, RENDER_DISTANCE, UNLOAD_DISTANCE]);

  // Initialize audio element (Subtask 8.1)
  // Requirements: 7.1, 10.4
  useEffect(() => {
    // Create global audio element
    const audio = new Audio();
    audio.preload = 'auto';
    
    // Set audio source if provided
    if (audioUrl) {
      audio.src = audioUrl;
    } else if (bootstrapData.audio_url) {
      audio.src = bootstrapData.audio_url;
    }
    
    // Audio event listeners
    audio.addEventListener('timeupdate', () => {
      setAudioState(prev => ({
        ...prev,
        currentTime: audio.currentTime
      }));
    });
    
    audio.addEventListener('play', () => {
      setAudioState(prev => ({
        ...prev,
        isPlaying: true
      }));
    });
    
    audio.addEventListener('pause', () => {
      setAudioState(prev => ({
        ...prev,
        isPlaying: false
      }));
    });
    
    audio.addEventListener('ended', () => {
      setAudioState(prev => ({
        ...prev,
        isPlaying: false,
        currentCardIndex: -1
      }));
    });
    
    audioRef.current = audio;
    setAudioState(prev => ({
      ...prev,
      audioElement: audio
    }));
    
    // Cleanup on unmount (Subtask 13.3)
    // Requirements: 12.1, 12.2
    return () => {
      if (audioCheckIntervalRef.current) {
        clearInterval(audioCheckIntervalRef.current);
      }
      audio.pause();
      audio.src = '';
      
      // Cleanup performance monitor
      performanceMonitorRef.current.destroy();
    };
  }, [audioUrl, bootstrapData.audio_url]);

  // ===== MEDIA PRELOADING =====
  
  /**
   * Preload media for next 2 cards
   * Requirements: 11.6
   */
  const preloadNextMedia = useCallback(() => {
    const preloadRange = [currentCardIndex + 1, currentCardIndex + 2];
    
    preloadRange.forEach(index => {
      if (index < cards.length && !preloadedMedia.has(index)) {
        const card = cards[index];
        
        if (card.mediaType === 'video') {
          const video = document.createElement('video');
          video.src = card.mediaUrl;
          video.preload = 'auto';
          video.load();
          preloadedMedia.set(index, video);
        } else {
          const img = new Image();
          img.src = card.mediaUrl;
          preloadedMedia.set(index, img);
        }
      }
    });
  }, [currentCardIndex, cards, preloadedMedia]);

  // Preload media when current card changes
  useEffect(() => {
    if (cards.length > 0) {
      preloadNextMedia();
    }
  }, [currentCardIndex, cards, preloadNextMedia]);

  // ===== CARD NAVIGATION (Subtask 7.2) =====
  
  /**
   * Navigate to next card with animation
   * Pauses audio on manual navigation
   * Requirements: 1.2, 1.4, 10.2, 12.1
   */
  const nextCard = useCallback(() => {
    if (isTransitioning || currentCardIndex >= cards.length - 1) {
      return;
    }
    
    // Start tracking transition time (Subtask 13.3)
    // Requirements: 12.1
    performanceMonitorRef.current.startTransition();
    
    // Pause audio on manual card navigation (Subtask 8.2)
    // Requirements: 10.2
    if (audioState.isPlaying && audioRef.current) {
      audioRef.current.pause();
      if (audioCheckIntervalRef.current) {
        clearInterval(audioCheckIntervalRef.current);
        audioCheckIntervalRef.current = null;
      }
      setAudioState(prev => ({
        ...prev,
        isPlaying: false,
        currentCardIndex: -1
      }));
    }
    
    setIsTransitioning(true);
    const nextIndex = currentCardIndex + 1;
    setCurrentCardIndex(nextIndex);
    
    // Reset transition state after animation completes
    setTimeout(() => {
      setIsTransitioning(false);
      
      // End tracking transition time (Subtask 13.3)
      // Requirements: 12.1
      const transitionTime = performanceMonitorRef.current.endTransition(nextIndex);
      
      // Start tracking media load for next card
      if (nextIndex < cards.length) {
        const nextCard = cards[nextIndex];
        performanceMonitorRef.current.startMediaLoad(nextCard.mediaUrl);
      }
    }, 500); // Match animation duration
  }, [isTransitioning, currentCardIndex, cards, audioState.isPlaying]);

  /**
   * Navigate to previous card
   * Pauses audio on manual navigation
   * Requirements: 1.2, 1.4, 10.2, 12.1
   */
  const previousCard = useCallback(() => {
    if (isTransitioning || currentCardIndex <= 0) {
      return;
    }
    
    // Start tracking transition time (Subtask 13.3)
    // Requirements: 12.1
    performanceMonitorRef.current.startTransition();
    
    // Pause audio on manual card navigation (Subtask 8.2)
    // Requirements: 10.2
    if (audioState.isPlaying && audioRef.current) {
      audioRef.current.pause();
      if (audioCheckIntervalRef.current) {
        clearInterval(audioCheckIntervalRef.current);
        audioCheckIntervalRef.current = null;
      }
      setAudioState(prev => ({
        ...prev,
        isPlaying: false,
        currentCardIndex: -1
      }));
    }
    
    setIsTransitioning(true);
    const prevIndex = currentCardIndex - 1;
    setCurrentCardIndex(prevIndex);
    
    // Reset transition state after animation completes
    setTimeout(() => {
      setIsTransitioning(false);
      
      // End tracking transition time (Subtask 13.3)
      // Requirements: 12.1
      performanceMonitorRef.current.endTransition(prevIndex);
    }, 500); // Match animation duration
  }, [isTransitioning, currentCardIndex, audioState.isPlaying]);



  // ===== SWIPE GESTURE HANDLING (Subtask 7.4) =====
  
  /**
   * Configure swipe handlers
   * Requirements: 1.4
   */
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => nextCard(),
    onSwipedRight: () => previousCard(),
    trackMouse: true, // Enable mouse swipe for desktop testing
    delta: 50, // 50px threshold
    swipeDuration: 500,
    preventScrollOnSwipe: true
  });

  // ===== EVENT HANDLERS =====
  
  /**
   * Handle tap/click to advance
   * Requirements: 1.2, 1.4
   */
  const handleCardTap = useCallback(() => {
    nextCard();
  }, [nextCard]);

  // ===== PER-CARD AUDIO PLAYBACK (Subtask 8.2) =====
  // Requirements: 10.1, 10.2
  
  /**
   * Handle audio play button click
   * Seeks to card's audio timestamp and starts playback
   * Requirements: 7.1, 10.1, 10.4
   */
  const handleAudioPlay = useCallback((cardIndex: number) => {
    const card = cards[cardIndex];
    const audio = audioRef.current;
    
    if (!card || !audio) {
      return;
    }
    
    // If already playing this card, pause it
    if (audioState.isPlaying && audioState.currentCardIndex === cardIndex) {
      audio.pause();
      if (audioCheckIntervalRef.current) {
        clearInterval(audioCheckIntervalRef.current);
        audioCheckIntervalRef.current = null;
      }
      setAudioState(prev => ({
        ...prev,
        isPlaying: false,
        currentCardIndex: -1
      }));
      return;
    }
    
    // Seek to card's audio timestamp
    audio.currentTime = card.audioTimestamp;
    
    // Update audio state
    setAudioState(prev => ({
      ...prev,
      currentCardIndex: cardIndex,
      currentTime: card.audioTimestamp
    }));
    
    // Start playback
    audio.play().catch(error => {
      console.error('Audio playback failed:', error);
    });
    
    // Clear any existing interval
    if (audioCheckIntervalRef.current) {
      clearInterval(audioCheckIntervalRef.current);
    }
    
    // Auto-advance to next card when segment ends
    // Requirements: 10.2
    const segmentEndTime = card.audioTimestamp + card.estimatedDuration;
    audioCheckIntervalRef.current = setInterval(() => {
      if (audio.currentTime >= segmentEndTime) {
        // Clear interval
        if (audioCheckIntervalRef.current) {
          clearInterval(audioCheckIntervalRef.current);
          audioCheckIntervalRef.current = null;
        }
        
        // Pause audio
        audio.pause();
        
        // Auto-advance to next card
        if (cardIndex < cards.length - 1) {
          nextCard();
        }
      }
    }, 100); // Check every 100ms
  }, [cards, audioState.isPlaying, audioState.currentCardIndex, nextCard]);

  // Get current card
  const currentCard = cards[currentCardIndex];

  /**
   * Handle keyboard navigation (arrow keys, space/enter for audio, escape for modals)
   * Requirements: 1.2, 1.4, 13.5
   */
  useEffect(() => {
    if (!currentCard) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowRight':
        case 'ArrowDown':
          event.preventDefault();
          nextCard();
          break;
        case 'ArrowLeft':
        case 'ArrowUp':
          event.preventDefault();
          previousCard();
          break;
        case ' ':
        case 'Enter':
          // Space/Enter for audio playback on story cards (not overview)
          if (currentCard.type !== 'overview') {
            event.preventDefault();
            handleAudioPlay(currentCardIndex);
          }
          break;
        case 'Escape':
          // Escape for closing modals or pausing audio
          event.preventDefault();
          if (audioState.isPlaying && audioRef.current) {
            audioRef.current.pause();
            if (audioCheckIntervalRef.current) {
              clearInterval(audioCheckIntervalRef.current);
              audioCheckIntervalRef.current = null;
            }
            setAudioState(prev => ({
              ...prev,
              isPlaying: false,
              currentCardIndex: -1
            }));
          }
          break;
        case 'p':
        case 'P':
          // Toggle performance overlay with 'P' key (Subtask 13.3)
          // Requirements: 12.1, 12.2
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            setShowPerformanceOverlay(prev => !prev);
            if (!showPerformanceOverlay) {
              performanceMonitorRef.current.logPerformanceReport();
            }
          }
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [nextCard, previousCard, currentCard, currentCardIndex, handleAudioPlay, audioState.isPlaying, showPerformanceOverlay]);

  // ===== RENDER =====
  
  if (cards.length === 0) {
    return (
      <div className="curio-card-stack curio-card-stack--loading">
        <div className="curio-card-stack__loader">Loading your stories...</div>
      </div>
    );
  }

  if (!currentCard) {
    return (
      <div className="curio-card-stack curio-card-stack--loading">
        <div className="curio-card-stack__loader">Loading card...</div>
      </div>
    );
  }

  /**
   * Check if a card should be rendered based on lazy loading logic
   * Requirements: 11.6
   */
  const shouldRenderCard = (index: number): boolean => {
    return renderedCardIndices.has(index);
  };

  return (
    <div 
      className="curio-card-stack"
      {...swipeHandlers}
      role="region"
      aria-label="Story cards carousel"
      aria-live="polite"
      aria-atomic="true"
      aria-describedby="card-navigation-instructions"
    >
      {/* Screen reader instructions */}
      <div id="card-navigation-instructions" className="sr-only">
        Use arrow keys to navigate between cards. Press Space or Enter to play audio narration. Press Escape to pause audio.
      </div>

      {/* Announce card transitions for screen readers */}
      <div className="sr-only" aria-live="assertive" aria-atomic="true">
        {currentCard.type === 'overview' 
          ? `Overview card. ${cards.length - 1} stories available.`
          : `Story ${currentCardIndex} of ${cards.length - 1}: ${currentCard.title}. ${currentCard.category} category.`
        }
      </div>

      {/* AnimatePresence for card transitions (Subtask 7.3) */}
      {/* Only render cards within RENDER_DISTANCE (Subtask 13.1) */}
      <AnimatePresence mode="wait" initial={false}>
        {shouldRenderCard(currentCardIndex) && (
          <motion.div
            key={currentCard.id}
            className="curio-card-stack__card-wrapper"
            variants={cardVariants}
            initial="enter"
            animate="center"
            exit="exit"
            role="group"
            aria-roledescription="card"
            aria-label={currentCard.type === 'overview' 
              ? 'Overview card' 
              : `Story card: ${currentCard.title}`
            }
          >
            <Suspense fallback={
              <div className="curio-card-stack__card-loading">
                <div className="curio-card-stack__card-spinner" />
              </div>
            }>
              {currentCard.type === 'overview' ? (
                <OverviewCard
                  date={new Date().toISOString()}
                  highlights={cards.slice(1, 7).map(card => 
                    `${card.title}`
                  )}
                  totalStories={cards.length - 1}
                  backgroundImage={currentCard.mediaUrl}
                  onTap={handleCardTap}
                />
              ) : (
                <StoryCard
                  story={{
                    title: currentCard.title,
                    summary: currentCard.summary,
                    url: '',
                    source: currentCard.source,
                    published_at: new Date().toISOString(),
                    category: currentCard.category,
                    image_url: currentCard.mediaUrl
                  }}
                  categoryType={currentCard.type}
                  scriptSegment={currentCard.scriptSegment}
                  estimatedDuration={currentCard.estimatedDuration}
                  mediaUrl={currentCard.mediaUrl}
                  mediaType={currentCard.mediaType}
                  onAudioPlay={() => handleAudioPlay(currentCardIndex)}
                  onTap={handleCardTap}
                  currentCardIndex={currentCardIndex}
                  totalCards={cards.length}
                  isAudioPlaying={audioState.isPlaying && audioState.currentCardIndex === currentCardIndex}
                />
              )}
            </Suspense>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress indicator */}
      <div className="curio-card-stack__progress" aria-hidden="true">
        <div 
          className="curio-card-stack__progress-bar"
          style={{ width: `${((currentCardIndex + 1) / cards.length) * 100}%` }}
          role="progressbar"
          aria-valuenow={currentCardIndex + 1}
          aria-valuemin={1}
          aria-valuemax={cards.length}
          aria-label={`Progress: Card ${currentCardIndex + 1} of ${cards.length}`}
        />
      </div>

      {/* Navigation hint (only show on first card) */}
      {currentCardIndex === 0 && (
        <div className="curio-card-stack__hint" aria-hidden="true">
          <span className="curio-card-stack__hint-text">
            Swipe or tap to navigate
          </span>
        </div>
      )}

      {/* Performance Overlay (Subtask 13.3) */}
      {/* Requirements: 12.1, 12.2 */}
      {showPerformanceOverlay && (
        <div className="curio-card-stack__performance-overlay" role="complementary" aria-label="Performance metrics">
          <div className="curio-card-stack__performance-header">
            <h3>Performance Metrics</h3>
            <button
              onClick={() => setShowPerformanceOverlay(false)}
              aria-label="Close performance overlay"
              className="curio-card-stack__performance-close"
            >
              ×
            </button>
          </div>
          <div className="curio-card-stack__performance-content">
            <PerformanceOverlay monitor={performanceMonitorRef.current} />
          </div>
          <div className="curio-card-stack__performance-hint">
            Press Ctrl/Cmd + P to toggle
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Performance Overlay Component
 * Displays real-time performance metrics
 * Requirements: 12.1, 12.2
 */
interface PerformanceOverlayProps {
  monitor: typeof performanceMonitor;
}

const PerformanceOverlay: React.FC<PerformanceOverlayProps> = ({ monitor }) => {
  const [stats, setStats] = React.useState(monitor.getStats());
  const [memoryUsage, setMemoryUsage] = React.useState(monitor.getCurrentMemoryUsage());

  // Update stats every second
  React.useEffect(() => {
    const interval = setInterval(() => {
      setStats(monitor.getStats());
      setMemoryUsage(monitor.getCurrentMemoryUsage());
    }, 1000);

    return () => clearInterval(interval);
  }, [monitor]);

  const isAcceptable = monitor.isPerformanceAcceptable();

  return (
    <div className="performance-overlay">
      <div className="performance-overlay__status">
        <span className={`performance-overlay__indicator ${isAcceptable ? 'good' : 'warning'}`}>
          {isAcceptable ? '✓' : '⚠'}
        </span>
        <span className="performance-overlay__status-text">
          {isAcceptable ? 'Performance OK' : 'Performance Issues'}
        </span>
      </div>

      <div className="performance-overlay__metrics">
        <div className="performance-overlay__metric">
          <span className="performance-overlay__metric-label">Avg Transition:</span>
          <span className="performance-overlay__metric-value">
            {stats.averageTransitionTime.toFixed(0)}ms
          </span>
        </div>

        <div className="performance-overlay__metric">
          <span className="performance-overlay__metric-label">Avg Media Load:</span>
          <span className="performance-overlay__metric-value">
            {stats.averageMediaLoadTime.toFixed(0)}ms
          </span>
        </div>

        <div className="performance-overlay__metric">
          <span className="performance-overlay__metric-label">Memory Usage:</span>
          <span className="performance-overlay__metric-value">
            {memoryUsage.toFixed(1)}MB
          </span>
        </div>

        <div className="performance-overlay__metric">
          <span className="performance-overlay__metric-label">Peak Memory:</span>
          <span className="performance-overlay__metric-value">
            {stats.peakMemoryUsage.toFixed(1)}MB
          </span>
        </div>

        <div className="performance-overlay__metric">
          <span className="performance-overlay__metric-label">Total Transitions:</span>
          <span className="performance-overlay__metric-value">
            {stats.totalTransitions}
          </span>
        </div>

        <div className="performance-overlay__metric">
          <span className="performance-overlay__metric-label">Slow Transitions:</span>
          <span className="performance-overlay__metric-value">
            {stats.slowTransitions} ({stats.totalTransitions > 0 ? ((stats.slowTransitions / stats.totalTransitions) * 100).toFixed(1) : 0}%)
          </span>
        </div>
      </div>
    </div>
  );
};

export default CurioCardStack;
