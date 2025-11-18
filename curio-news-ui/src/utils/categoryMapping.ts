/**
 * Category Mapping and Configuration
 * Defines visual styling and mapping logic for story categories
 */

import { CategoryType, CategoryConfig } from '../components/cards/types';

/**
 * Category configuration mapping
 * Defines gradients, icons, and labels for each category type
 */
export const categoryConfig: Record<CategoryType, CategoryConfig> = {
  favorite: {
    gradient: 'from-pink-500 to-rose-500',
    icon: 'Heart',
    label: 'FAVORITE'
  },
  world: {
    gradient: 'from-blue-500 to-indigo-500',
    icon: 'Globe',
    label: 'WORLD'
  },
  local: {
    gradient: 'from-green-500 to-emerald-500',
    icon: 'MapPin',
    label: 'LOCAL'
  },
  event: {
    gradient: 'from-purple-500 to-violet-500',
    icon: 'Calendar',
    label: 'EVENT'
  },
  movie: {
    gradient: 'from-red-500 to-orange-500',
    icon: 'Film',
    label: 'MOVIE'
  },
  music: {
    gradient: 'from-cyan-500 to-blue-500',
    icon: 'Music',
    label: 'MUSIC'
  },
  book: {
    gradient: 'from-amber-500 to-yellow-500',
    icon: 'Book',
    label: 'BOOK'
  }
};

/**
 * Map news category strings to CategoryType
 * Handles various category naming conventions from different sources
 * 
 * @param category - Category string from news API or agent output
 * @returns Mapped CategoryType
 */
export function mapNewsCategory(category?: string): CategoryType {
  if (!category) {
    return 'world'; // Default category
  }

  const normalized = category.toLowerCase().trim();

  // Direct matches
  if (normalized === 'favorite' || normalized === 'favourite') {
    return 'favorite';
  }
  if (normalized === 'world' || normalized === 'international' || normalized === 'global') {
    return 'world';
  }
  if (normalized === 'local' || normalized === 'regional' || normalized === 'city') {
    return 'local';
  }
  if (normalized === 'event' || normalized === 'events' || normalized === 'happening') {
    return 'event';
  }
  if (normalized === 'movie' || normalized === 'movies' || normalized === 'film' || normalized === 'cinema') {
    return 'movie';
  }
  if (normalized === 'music' || normalized === 'audio' || normalized === 'concert') {
    return 'music';
  }
  if (normalized === 'book' || normalized === 'books' || normalized === 'literature' || normalized === 'reading') {
    return 'book';
  }

  // Keyword-based matching
  if (normalized.includes('entertainment') || normalized.includes('culture')) {
    return 'event';
  }
  if (normalized.includes('tech') || normalized.includes('science') || normalized.includes('business')) {
    return 'world';
  }
  if (normalized.includes('sport') || normalized.includes('health') || normalized.includes('lifestyle')) {
    return 'local';
  }

  // Default fallback
  return 'world';
}

/**
 * Map entertainment type to CategoryType
 * @param type - Entertainment type from Entertainment Curator agent
 * @returns Mapped CategoryType
 */
export function mapEntertainmentType(type: 'movie' | 'music' | 'book'): CategoryType {
  return type; // Direct mapping
}

/**
 * Get category emoji for overview highlights
 * @param category - CategoryType
 * @returns Emoji string
 */
export function getCategoryEmoji(category: CategoryType): string {
  const emojiMap: Record<CategoryType, string> = {
    favorite: '❤️',
    world: '🌍',
    local: '📍',
    event: '📅',
    movie: '🎬',
    music: '🎵',
    book: '📚'
  };
  return emojiMap[category];
}

/**
 * Get category color for placeholders and fallbacks
 * @param category - CategoryType
 * @returns Hex color code
 */
export function getCategoryColor(category: CategoryType): string {
  const colorMap: Record<CategoryType, string> = {
    favorite: '#ec4899', // pink-500
    world: '#3b82f6',    // blue-500
    local: '#10b981',    // green-500
    event: '#a855f7',    // purple-500
    movie: '#ef4444',    // red-500
    music: '#06b6d4',    // cyan-500
    book: '#f59e0b'      // amber-500
  };
  return colorMap[category];
}

/**
 * Get Unsplash search keywords for category
 * Used for fallback image generation
 * 
 * @param category - CategoryType
 * @returns Array of search keywords
 */
export function getCategoryKeywords(category: CategoryType): string[] {
  const keywordMap: Record<CategoryType, string[]> = {
    favorite: ['featured', 'highlight', 'special', 'star'],
    world: ['world', 'global', 'international', 'earth'],
    local: ['city', 'local', 'community', 'neighborhood'],
    event: ['event', 'happening', 'festival', 'celebration'],
    movie: ['cinema', 'film', 'movie', 'theater'],
    music: ['music', 'concert', 'performance', 'audio'],
    book: ['book', 'reading', 'literature', 'library']
  };
  return keywordMap[category];
}

/**
 * Determine category from story content
 * Uses title and summary to infer category when not explicitly provided
 * 
 * @param title - Story title
 * @param summary - Story summary
 * @param source - Story source
 * @returns Inferred CategoryType
 */
export function inferCategory(title: string, summary: string, source?: string): CategoryType {
  const text = `${title} ${summary}`.toLowerCase();

  // Entertainment keywords
  if (text.match(/\b(movie|film|cinema|actor|director|box office)\b/)) {
    return 'movie';
  }
  if (text.match(/\b(music|song|album|artist|concert|band|singer)\b/)) {
    return 'music';
  }
  if (text.match(/\b(book|author|novel|publish|literature|writer)\b/)) {
    return 'book';
  }

  // Event keywords
  if (text.match(/\b(event|festival|conference|summit|ceremony|celebration)\b/)) {
    return 'event';
  }

  // Local keywords
  if (text.match(/\b(local|city|town|community|neighborhood|mayor)\b/)) {
    return 'local';
  }

  // Default to world news
  return 'world';
}

/**
 * Get all available categories
 * @returns Array of all CategoryType values
 */
export function getAllCategories(): CategoryType[] {
  return ['favorite', 'world', 'local', 'event', 'movie', 'music', 'book'];
}

/**
 * Validate category type
 * @param category - Category string to validate
 * @returns true if valid CategoryType
 */
export function isValidCategory(category: string): category is CategoryType {
  return getAllCategories().includes(category as CategoryType);
}
