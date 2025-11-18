/**
 * Type definitions for the mobile card UI redesign
 * These interfaces define the data structures for card-based news presentation
 */

// Category types for story cards
export type CategoryType = 
  | 'favorite' 
  | 'world' 
  | 'local' 
  | 'event' 
  | 'movie' 
  | 'music' 
  | 'book';

// Media types supported for card backgrounds
export type MediaType = 'video' | 'image' | 'gif';

// Card type discriminator
export type CardType = 'overview' | CategoryType;

/**
 * Main story card data structure
 * Represents a single swipeable card in the UI
 */
export interface StoryCard {
  id: number;
  type: CardType;
  title: string;
  summary: string;
  scriptSegment: string;
  estimatedDuration: number; // Duration in seconds
  mediaUrl: string;
  mediaType: MediaType;
  fallbackImage: string;
  category: string;
  source: string;
  audioTimestamp: number; // Start time in full audio (seconds)
}

/**
 * Script segment with timing information
 * Used to split long scripts into card-sized chunks
 */
export interface ScriptSegment {
  text: string;
  duration: number; // Duration in seconds
  startTime: number; // Start time in seconds
  endTime: number; // End time in seconds
}

/**
 * Word timing data from Script Writer agent
 * Used for precise script segmentation
 */
export interface WordTiming {
  word: string;
  start: number; // Start time in seconds
  end: number; // End time in seconds
}

/**
 * Category configuration for visual styling
 * Defines gradients, icons, and labels for each category
 */
export interface CategoryConfig {
  gradient: string; // Tailwind gradient classes
  icon: string; // Lucide icon name
  label: string; // Display label
}

/**
 * Props for CurioCardStack component
 */
export interface CurioCardStackProps {
  newsItems: NewsItem[];
  agentOutputs: AgentOutputs;
  script: string;
  wordTimings: WordTiming[];
  onAudioPlay: (cardIndex: number) => void;
}

/**
 * State for CurioCardStack component
 */
export interface CardStackState {
  currentCardIndex: number;
  cards: StoryCard[];
  isTransitioning: boolean;
  preloadedMedia: Map<number, HTMLVideoElement | HTMLImageElement>;
}

/**
 * Props for OverviewCard component
 */
export interface OverviewCardProps {
  date: string;
  highlights: string[];
  totalStories: number;
  backgroundImage: string;
  onTap: () => void;
}

/**
 * Props for StoryCard component
 */
export interface StoryCardProps {
  story: NewsItem;
  categoryType: CategoryType;
  scriptSegment: string;
  estimatedDuration: number;
  mediaUrl: string;
  mediaType: MediaType;
  onAudioPlay: () => void;
  onTap: () => void;
  isAudioPlaying?: boolean;
}

/**
 * Props for BackgroundMedia component
 */
export interface BackgroundMediaProps {
  mediaUrl: string;
  mediaType: MediaType;
  fallbackImage: string;
  alt: string;
}

/**
 * Props for CategoryTag component
 */
export interface CategoryTagProps {
  category: CategoryType;
}

/**
 * News item structure from API
 */
export interface NewsItem {
  title: string;
  summary: string;
  url: string;
  source: string;
  published_at: string;
  category?: string;
  image_url?: string;
  social_impact_score?: number;
}

/**
 * Agent outputs from Bedrock orchestrator
 */
export interface AgentOutputs {
  favoriteStory?: FavoriteStory;
  curatedStories?: NewsItem[];
  mediaEnhancements?: MediaEnhancement[];
  weekendRecommendations?: Entertainment[];
  socialImpactScores?: Record<string, number>;
}

/**
 * Favorite story from Story Selector agent
 */
export interface FavoriteStory {
  title: string;
  summary: string;
  reason: string;
  source: string;
  url: string;
  image_url?: string;
}

/**
 * Media enhancement from Media Enhancer agent
 */
export interface MediaEnhancement {
  story_title: string;
  media_url: string;
  media_type: MediaType;
  fallback_url?: string;
  keywords?: string[];
}

/**
 * Entertainment recommendation structure
 */
export interface Entertainment {
  type: 'movie' | 'music' | 'book';
  title: string;
  description: string;
  image_url?: string;
  rating?: number;
  genre?: string;
}

/**
 * Bootstrap API response structure
 */
export interface BootstrapResponse {
  news_items: NewsItem[];
  script: string;
  word_timings: WordTiming[];
  agentOutputs?: AgentOutputs;
  audio_url?: string;
}

/**
 * Audio state management
 */
export interface AudioState {
  isPlaying: boolean;
  currentCardIndex: number;
  audioElement: HTMLAudioElement | null;
  currentTime: number;
}

/**
 * Swipe configuration for gesture handling
 */
export interface SwipeConfig {
  onSwipeLeft: () => void;
  onSwipeRight: () => void;
  swipeThreshold: number; // pixels
  swipeVelocityThreshold: number;
}

/**
 * Framer Motion animation variants
 */
export interface CardAnimationVariants {
  enter: {
    opacity: number;
    y: number;
    scale: number;
  };
  center: {
    opacity: number;
    y: number;
    scale: number;
    transition: {
      duration: number;
      ease: number[];
    };
  };
  exit: {
    opacity: number;
    y: number;
    scale: number;
    transition: {
      duration: number;
    };
  };
}
