/**
 * Card Data Transformer
 * Transforms Bedrock agent outputs into StoryCard format
 * for the mobile card UI
 */

import {
  StoryCard,
  BootstrapResponse,
  NewsItem,
  AgentOutputs,
  MediaEnhancement,
  Entertainment,
  CategoryType
} from '../components/cards/types';
import { segmentScript, fallbackSegmentation, generateSegmentsFromSummaries } from './scriptSegmentation';
import {
  mapNewsCategory,
  mapEntertainmentType,
  getCategoryEmoji,
  getCategoryKeywords,
  inferCategory
} from './categoryMapping';

/**
 * Generate Unsplash URL for fallback images
 * @param keywords - Search keywords
 * @param title - Story title for deterministic hash
 * @returns Unsplash image URL
 */
function generateUnsplashUrl(keywords: string[], title: string): string {
  // Create deterministic hash from title
  const hash = title.split('').reduce((acc, char) => {
    return ((acc << 5) - acc) + char.charCodeAt(0);
  }, 0);
  
  const keywordString = keywords.join(',');
  return `https://source.unsplash.com/800x400/?${keywordString}&sig=${Math.abs(hash)}`;
}

/**
 * Generate placeholder image URL
 * @param category - CategoryType
 * @param title - Story title
 * @returns Placeholder image URL
 */
function generatePlaceholderUrl(category: CategoryType, title: string): string {
  const emoji = getCategoryEmoji(category);
  const text = encodeURIComponent(emoji);
  return `https://via.placeholder.com/800x400/1f2937/ffffff?text=${text}`;
}

/**
 * Find media enhancement for a story
 * @param title - Story title
 * @param mediaEnhancements - Array of media enhancements from agent
 * @returns Matching media enhancement or undefined
 */
function findMediaEnhancement(
  title: string,
  mediaEnhancements?: MediaEnhancement[]
): MediaEnhancement | undefined {
  if (!mediaEnhancements || mediaEnhancements.length === 0) {
    return undefined;
  }

  // Try exact match first
  const exactMatch = mediaEnhancements.find(
    m => m.story_title.toLowerCase() === title.toLowerCase()
  );
  if (exactMatch) {
    return exactMatch;
  }

  // Try partial match
  const partialMatch = mediaEnhancements.find(
    m => title.toLowerCase().includes(m.story_title.toLowerCase()) ||
         m.story_title.toLowerCase().includes(title.toLowerCase())
  );
  return partialMatch;
}

/**
 * Create overview card (first card in sequence)
 * @param bootstrapData - Bootstrap API response
 * @returns Overview StoryCard
 */
export function createOverviewCard(bootstrapData: BootstrapResponse): StoryCard {
  const date = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  // Generate highlights from news items
  const highlights = bootstrapData.news_items.slice(0, 6).map((item, index) => {
    const category = mapNewsCategory(item.category);
    const emoji = getCategoryEmoji(category);
    return `${emoji} ${item.title}`;
  });

  const totalStories = bootstrapData.news_items.length;

  return {
    id: 0,
    type: 'overview',
    title: 'Today in Curio 🪄',
    summary: `${totalStories} stories curated just for you`,
    scriptSegment: `Welcome to Curio. Today we have ${totalStories} stories covering world news, local events, and entertainment. Tap to begin your personalized news experience.`,
    estimatedDuration: 10,
    mediaUrl: 'https://source.unsplash.com/800x400/?news,morning,coffee&sig=overview',
    mediaType: 'image',
    fallbackImage: 'https://source.unsplash.com/800x400/?abstract,gradient&sig=overview',
    category: 'overview',
    source: 'Curio',
    audioTimestamp: 0
  };
}

/**
 * Create favorite story card from Story Selector agent output
 * @param favoriteStory - Favorite story from agent
 * @param script - Full script text
 * @param wordTimings - Word timing data
 * @param mediaEnhancements - Media enhancements from agent
 * @returns Favorite StoryCard
 */
export function createFavoriteCard(
  favoriteStory: any,
  script: string,
  wordTimings: any[],
  mediaEnhancements?: MediaEnhancement[]
): StoryCard {
  // Segment the script with fallback handling
  let segments: any[] = [];
  
  try {
    if (wordTimings && wordTimings.length > 0 && script) {
      segments = segmentScript(script, wordTimings);
    } else if (script) {
      segments = fallbackSegmentation(script);
    }
  } catch (error) {
    console.error('Error segmenting script for favorite card:', error);
  }

  // Use first segment for favorite story, or generate from summary
  const segment = segments[0] || {
    text: `${favoriteStory.title}. ${favoriteStory.summary}`,
    duration: 20,
    startTime: 0,
    endTime: 20
  };

  // Find media enhancement
  const media = findMediaEnhancement(favoriteStory.title, mediaEnhancements);
  const categoryKeywords = getCategoryKeywords('favorite');

  return {
    id: 1,
    type: 'favorite',
    title: favoriteStory.title,
    summary: favoriteStory.summary,
    scriptSegment: segment.text,
    estimatedDuration: segment.duration,
    mediaUrl: media?.media_url || favoriteStory.image_url || generateUnsplashUrl(categoryKeywords, favoriteStory.title),
    mediaType: media?.media_type || 'image',
    fallbackImage: media?.fallback_url || generateUnsplashUrl(categoryKeywords, favoriteStory.title),
    category: 'favorite',
    source: favoriteStory.source || 'Curio',
    audioTimestamp: segment.startTime
  };
}

/**
 * Create story card from news item
 * @param newsItem - News item from API
 * @param scriptSegment - Script segment for this card
 * @param segmentIndex - Index of this segment
 * @param mediaEnhancements - Media enhancements from agent
 * @returns StoryCard
 */
export function createStoryCard(
  newsItem: NewsItem,
  scriptSegment: { text: string; duration: number; startTime: number; endTime: number },
  segmentIndex: number,
  mediaEnhancements?: MediaEnhancement[]
): StoryCard {
  // Determine category
  const category = newsItem.category
    ? mapNewsCategory(newsItem.category)
    : inferCategory(newsItem.title, newsItem.summary, newsItem.source);

  // Find media enhancement
  const media = findMediaEnhancement(newsItem.title, mediaEnhancements);
  const categoryKeywords = getCategoryKeywords(category);

  // Generate fallback URLs
  const unsplashUrl = generateUnsplashUrl(categoryKeywords, newsItem.title);
  const placeholderUrl = generatePlaceholderUrl(category, newsItem.title);

  return {
    id: segmentIndex + 2, // +2 to account for overview and favorite cards
    type: category,
    title: newsItem.title,
    summary: newsItem.summary,
    scriptSegment: scriptSegment.text,
    estimatedDuration: scriptSegment.duration,
    mediaUrl: media?.media_url || newsItem.image_url || unsplashUrl,
    mediaType: media?.media_type || 'image',
    fallbackImage: media?.fallback_url || newsItem.image_url || unsplashUrl,
    category: newsItem.category || category,
    source: newsItem.source,
    audioTimestamp: scriptSegment.startTime
  };
}

/**
 * Create entertainment card from Entertainment Curator recommendation
 * @param entertainment - Entertainment recommendation
 * @param index - Index for card ID
 * @param audioTimestamp - Audio timestamp for this card
 * @returns StoryCard
 */
export function createEntertainmentCard(
  entertainment: Entertainment,
  index: number,
  audioTimestamp: number
): StoryCard {
  const category = mapEntertainmentType(entertainment.type);
  const categoryKeywords = getCategoryKeywords(category);

  // Generate script segment for entertainment
  const scriptText = `${entertainment.title}. ${entertainment.description}${entertainment.genre ? ` Genre: ${entertainment.genre}.` : ''}${entertainment.rating ? ` Rating: ${entertainment.rating} stars.` : ''}`;
  
  // Estimate duration based on word count
  const wordCount = scriptText.split(/\s+/).length;
  const duration = Math.max(15, Math.min(30, wordCount / 2.5)); // 2.5 words per second

  return {
    id: index,
    type: category,
    title: entertainment.title,
    summary: entertainment.description,
    scriptSegment: scriptText,
    estimatedDuration: duration,
    mediaUrl: entertainment.image_url || generateUnsplashUrl(categoryKeywords, entertainment.title),
    mediaType: 'image',
    fallbackImage: generateUnsplashUrl(categoryKeywords, entertainment.title),
    category: entertainment.type,
    source: 'Entertainment Curator',
    audioTimestamp: audioTimestamp
  };
}

/**
 * Main transformer function
 * Converts bootstrap API response into array of StoryCards
 * 
 * @param bootstrapData - Bootstrap API response
 * @returns Array of StoryCards ready for display
 */
export function transformToCards(bootstrapData: BootstrapResponse): StoryCard[] {
  const cards: StoryCard[] = [];

  // 1. Create overview card
  cards.push(createOverviewCard(bootstrapData));

  // 2. Segment the script with comprehensive fallback handling
  let segments: any[] = [];
  
  try {
    if (bootstrapData.word_timings && bootstrapData.word_timings.length > 0 && bootstrapData.script) {
      // Primary: Use word timings for accurate segmentation
      segments = segmentScript(bootstrapData.script, bootstrapData.word_timings);
    } else if (bootstrapData.script) {
      // Secondary: Use script without timings
      segments = fallbackSegmentation(bootstrapData.script);
    } else if (bootstrapData.news_items && bootstrapData.news_items.length > 0) {
      // Tertiary: Generate from news summaries
      console.warn('No script available, generating segments from news summaries');
      segments = generateSegmentsFromSummaries(bootstrapData.news_items);
    }
  } catch (error) {
    console.error('Error segmenting script, falling back to news summaries:', error);
    if (bootstrapData.news_items && bootstrapData.news_items.length > 0) {
      segments = generateSegmentsFromSummaries(bootstrapData.news_items);
    }
  }

  // Ensure we have at least some segments
  if (segments.length === 0) {
    console.warn('No segments generated, using default segment');
    segments = [{
      text: 'Welcome to your personalized news briefing.',
      duration: 20,
      startTime: 0,
      endTime: 20
    }];
  }

  // 3. Create favorite story card (if available)
  if (bootstrapData.agentOutputs?.favoriteStory) {
    cards.push(createFavoriteCard(
      bootstrapData.agentOutputs.favoriteStory,
      bootstrapData.script,
      bootstrapData.word_timings,
      bootstrapData.agentOutputs.mediaEnhancements
    ));
  }

  // 4. Create story cards from curated news
  const newsItems = bootstrapData.agentOutputs?.curatedStories || bootstrapData.news_items;
  
  // Skip first segment if used for favorite story
  const startSegmentIndex = bootstrapData.agentOutputs?.favoriteStory ? 1 : 0;
  
  newsItems.forEach((item, index) => {
    try {
      const segmentIndex = startSegmentIndex + index;
      
      // Use corresponding segment or create fallback from item
      let segment = segments[segmentIndex];
      
      if (!segment) {
        console.warn(`No segment available for story ${index}, generating from summary`);
        const text = `${item.title}. ${item.summary}`;
        const wordCount = text.split(/\s+/).length;
        const duration = Math.max(15, Math.min(30, wordCount / 2.5));
        
        segment = {
          text: text,
          duration: duration,
          startTime: segmentIndex * 20,
          endTime: segmentIndex * 20 + duration
        };
      }

      cards.push(createStoryCard(
        item,
        segment,
        index,
        bootstrapData.agentOutputs?.mediaEnhancements
      ));
    } catch (error) {
      console.error(`Error creating story card for item ${index}:`, error);
      // Continue with next item instead of failing completely
    }
  });

  // 5. Create entertainment cards (if available)
  if (bootstrapData.agentOutputs?.weekendRecommendations) {
    try {
      const lastSegment = segments[segments.length - 1];
      let audioTimestamp = lastSegment ? lastSegment.endTime : cards.length * 20;

      bootstrapData.agentOutputs.weekendRecommendations.forEach((entertainment, index) => {
        try {
          const card = createEntertainmentCard(
            entertainment,
            cards.length,
            audioTimestamp
          );
          cards.push(card);
          audioTimestamp += card.estimatedDuration;
        } catch (error) {
          console.error(`Error creating entertainment card ${index}:`, error);
        }
      });
    } catch (error) {
      console.error('Error processing entertainment recommendations:', error);
    }
  }

  // Ensure we have at least the overview card
  if (cards.length === 0) {
    console.error('No cards generated, returning minimal overview card');
    return [createOverviewCard(bootstrapData)];
  }

  return cards;
}

/**
 * Transform single news item to card (utility function)
 * Useful for adding individual cards dynamically
 * 
 * @param newsItem - News item to transform
 * @param cardId - Unique card ID
 * @param audioTimestamp - Audio timestamp
 * @returns StoryCard
 */
export function transformNewsItemToCard(
  newsItem: NewsItem,
  cardId: number,
  audioTimestamp: number = 0
): StoryCard {
  const category = newsItem.category
    ? mapNewsCategory(newsItem.category)
    : inferCategory(newsItem.title, newsItem.summary, newsItem.source);

  const categoryKeywords = getCategoryKeywords(category);
  const scriptText = `${newsItem.title}. ${newsItem.summary}`;
  const wordCount = scriptText.split(/\s+/).length;
  const duration = Math.max(15, Math.min(30, wordCount / 2.5));

  return {
    id: cardId,
    type: category,
    title: newsItem.title,
    summary: newsItem.summary,
    scriptSegment: scriptText,
    estimatedDuration: duration,
    mediaUrl: newsItem.image_url || generateUnsplashUrl(categoryKeywords, newsItem.title),
    mediaType: 'image',
    fallbackImage: generateUnsplashUrl(categoryKeywords, newsItem.title),
    category: newsItem.category || category,
    source: newsItem.source,
    audioTimestamp: audioTimestamp
  };
}
