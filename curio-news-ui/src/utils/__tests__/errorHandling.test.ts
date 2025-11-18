/**
 * Error Handling Tests
 * Tests for media loading and script segmentation fallbacks
 */

import { segmentScript, fallbackSegmentation, generateSegmentsFromSummaries } from '../scriptSegmentation';

describe('Script Segmentation Error Handling', () => {
  describe('segmentScript with invalid inputs', () => {
    it('should handle empty word timings', () => {
      const script = 'This is a test script. It has multiple sentences.';
      const result = segmentScript(script, []);
      
      expect(result).toBeDefined();
      expect(result.length).toBeGreaterThan(0);
      expect(result[0].text).toBeTruthy();
    });

    it('should handle null word timings', () => {
      const script = 'This is a test script.';
      const result = segmentScript(script, null as any);
      
      expect(result).toBeDefined();
      expect(result.length).toBeGreaterThan(0);
    });

    it('should handle empty script', () => {
      const result = segmentScript('', []);
      
      expect(result).toBeDefined();
      expect(result.length).toBe(0);
    });

    it('should handle invalid word timing structure', () => {
      const script = 'Test script.';
      const invalidTimings = [
        { word: 'Test', start: 'invalid', end: 'invalid' } as any
      ];
      
      const result = segmentScript(script, invalidTimings);
      
      expect(result).toBeDefined();
      expect(result.length).toBeGreaterThan(0);
    });
  });

  describe('fallbackSegmentation', () => {
    it('should handle empty script', () => {
      const result = fallbackSegmentation('');
      
      expect(result).toBeDefined();
      expect(result.length).toBe(0);
    });

    it('should handle script without sentence boundaries', () => {
      const script = 'This is a script without proper punctuation';
      const result = fallbackSegmentation(script);
      
      expect(result).toBeDefined();
      expect(result.length).toBe(1);
      expect(result[0].text).toBe(script);
      expect(result[0].duration).toBeGreaterThan(0);
    });

    it('should create segments with minimum duration', () => {
      const script = 'Short. Very short.';
      const result = fallbackSegmentation(script);
      
      expect(result).toBeDefined();
      result.forEach(segment => {
        expect(segment.duration).toBeGreaterThanOrEqual(15);
      });
    });

    it('should handle null input', () => {
      const result = fallbackSegmentation(null as any);
      
      expect(result).toBeDefined();
      expect(result.length).toBe(0);
    });
  });

  describe('generateSegmentsFromSummaries', () => {
    it('should generate segments from news items', () => {
      const newsItems = [
        { title: 'Test Story 1', summary: 'This is a test summary.' },
        { title: 'Test Story 2', summary: 'Another test summary.' }
      ];
      
      const result = generateSegmentsFromSummaries(newsItems);
      
      expect(result).toBeDefined();
      expect(result.length).toBe(2);
      expect(result[0].text).toContain('Test Story 1');
      expect(result[1].text).toContain('Test Story 2');
    });

    it('should handle empty news items', () => {
      const result = generateSegmentsFromSummaries([]);
      
      expect(result).toBeDefined();
      expect(result.length).toBe(0);
    });

    it('should handle items with empty fields', () => {
      const newsItems = [
        { title: 'Valid Story', summary: 'Valid summary.' },
        { title: '', summary: '' },
        { title: 'Another Valid', summary: 'Another summary.' }
      ];
      
      const result = generateSegmentsFromSummaries(newsItems);
      
      expect(result).toBeDefined();
      // Empty items still create segments with just ". " which gets trimmed
      expect(result.length).toBeGreaterThanOrEqual(2);
    });

    it('should estimate duration based on word count', () => {
      const newsItems = [
        { 
          title: 'Long Story', 
          summary: 'This is a very long summary with many words that should result in a longer estimated duration for the segment.'
        }
      ];
      
      const result = generateSegmentsFromSummaries(newsItems);
      
      expect(result[0].duration).toBeGreaterThanOrEqual(15);
      expect(result[0].duration).toBeLessThanOrEqual(30);
    });
  });
});
