/**
 * Tests for core data transformation layer
 * Validates script segmentation, category mapping, and card transformation
 */

import {
  segmentScript,
  fallbackSegmentation,
  calculateTotalDuration,
  validateSegments
} from '../scriptSegmentation';
import {
  mapNewsCategory,
  getCategoryEmoji,
  inferCategory,
  isValidCategory
} from '../categoryMapping';
import {
  transformToCards,
  createOverviewCard,
  transformNewsItemToCard
} from '../cardTransformer';
import { WordTiming, BootstrapResponse, NewsItem } from '../../components/cards/types';

describe('Script Segmentation', () => {
  test('segments script with word timings', () => {
    const wordTimings: WordTiming[] = [
      { word: 'Hello', start: 0, end: 0.5 },
      { word: 'world.', start: 0.5, end: 1.0 },
      { word: 'This', start: 1.0, end: 1.3 },
      { word: 'is', start: 1.3, end: 1.5 },
      { word: 'a', start: 1.5, end: 1.6 },
      { word: 'test.', start: 1.6, end: 2.0 }
    ];

    const script = 'Hello world. This is a test.';
    const segments = segmentScript(script, wordTimings, 1.5);

    expect(segments.length).toBeGreaterThan(0);
    expect(segments[0].text).toBeTruthy();
    expect(segments[0].duration).toBeGreaterThan(0);
  });

  test('fallback segmentation works without timings', () => {
    const script = 'This is a test sentence. This is another sentence. And one more.';
    const segments = fallbackSegmentation(script, 20);

    expect(segments.length).toBeGreaterThan(0);
    expect(segments[0].text).toBeTruthy();
    expect(segments[0].duration).toBeGreaterThan(0);
  });

  test('calculates total duration correctly', () => {
    const wordTimings: WordTiming[] = [
      { word: 'Hello', start: 0, end: 0.5 },
      { word: 'world', start: 0.5, end: 1.0 }
    ];

    const duration = calculateTotalDuration(wordTimings);
    expect(duration).toBe(1.0);
  });

  test('validates segments correctly', () => {
    const validSegments = [
      { text: 'Test segment', duration: 20, startTime: 0, endTime: 20 }
    ];

    const result = validateSegments(validSegments);
    expect(result.valid).toBe(true);
    expect(result.issues.length).toBe(0);
  });
});

describe('Category Mapping', () => {
  test('maps news categories correctly', () => {
    expect(mapNewsCategory('world')).toBe('world');
    expect(mapNewsCategory('international')).toBe('world');
    expect(mapNewsCategory('movie')).toBe('movie');
    expect(mapNewsCategory('film')).toBe('movie');
    expect(mapNewsCategory(undefined)).toBe('world');
  });

  test('gets category emoji', () => {
    expect(getCategoryEmoji('favorite')).toBe('❤️');
    expect(getCategoryEmoji('world')).toBe('🌍');
    expect(getCategoryEmoji('movie')).toBe('🎬');
  });

  test('infers category from content', () => {
    expect(inferCategory('New movie release', 'A film about...')).toBe('movie');
    expect(inferCategory('Concert tonight', 'Music performance...')).toBe('music');
    expect(inferCategory('Book review', 'Author writes...')).toBe('book');
    expect(inferCategory('Breaking news', 'Global developments...')).toBe('world');
  });

  test('validates category types', () => {
    expect(isValidCategory('world')).toBe(true);
    expect(isValidCategory('movie')).toBe(true);
    expect(isValidCategory('invalid')).toBe(false);
  });
});

describe('Card Transformation', () => {
  const mockBootstrapData: BootstrapResponse = {
    news_items: [
      {
        title: 'Test News',
        summary: 'Test summary',
        url: 'https://test.com',
        source: 'Test Source',
        published_at: '2025-01-01',
        category: 'world'
      }
    ],
    script: 'This is a test script. It has multiple sentences.',
    word_timings: [
      { word: 'This', start: 0, end: 0.3 },
      { word: 'is', start: 0.3, end: 0.5 },
      { word: 'a', start: 0.5, end: 0.6 },
      { word: 'test', start: 0.6, end: 1.0 },
      { word: 'script.', start: 1.0, end: 1.5 }
    ]
  };

  test('creates overview card', () => {
    const card = createOverviewCard(mockBootstrapData);

    expect(card.id).toBe(0);
    expect(card.type).toBe('overview');
    expect(card.title).toContain('Curio');
    expect(card.mediaType).toBe('image');
  });

  test('transforms bootstrap data to cards', () => {
    const cards = transformToCards(mockBootstrapData);

    expect(cards.length).toBeGreaterThan(0);
    expect(cards[0].type).toBe('overview');
    expect(cards[0].id).toBe(0);
  });

  test('transforms single news item to card', () => {
    const newsItem: NewsItem = {
      title: 'Test Article',
      summary: 'Test summary',
      url: 'https://test.com',
      source: 'Test',
      published_at: '2025-01-01',
      category: 'world'
    };

    const card = transformNewsItemToCard(newsItem, 1, 0);

    expect(card.id).toBe(1);
    expect(card.title).toBe('Test Article');
    expect(card.type).toBe('world');
    expect(card.estimatedDuration).toBeGreaterThan(0);
  });

  test('handles missing agent outputs gracefully', () => {
    const minimalData: BootstrapResponse = {
      news_items: [
        {
          title: 'Test',
          summary: 'Summary',
          url: 'https://test.com',
          source: 'Test',
          published_at: '2025-01-01'
        }
      ],
      script: 'Test script.',
      word_timings: []
    };

    const cards = transformToCards(minimalData);

    expect(cards.length).toBeGreaterThan(0);
    expect(cards[0].type).toBe('overview');
  });
});
