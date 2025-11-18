/**
 * Utility functions for mobile card UI
 * Central export point for all card-related utilities
 */

// Script segmentation
export {
  segmentScript,
  fallbackSegmentation,
  calculateTotalDuration,
  validateSegments
} from './scriptSegmentation';

// Category mapping
export {
  categoryConfig,
  mapNewsCategory,
  mapEntertainmentType,
  getCategoryEmoji,
  getCategoryColor,
  getCategoryKeywords,
  inferCategory,
  getAllCategories,
  isValidCategory
} from './categoryMapping';

// Card transformation
export {
  transformToCards,
  transformNewsItemToCard,
  createOverviewCard,
  createFavoriteCard,
  createStoryCard,
  createEntertainmentCard
} from './cardTransformer';
