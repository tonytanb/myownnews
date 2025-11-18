/**
 * Script Segmentation Algorithm
 * Splits long scripts into 15-30 second segments using word timings
 * for optimal card-based presentation
 */

import { WordTiming, ScriptSegment } from '../components/cards/types';

/**
 * Check if a word represents a sentence boundary
 * @param word - The word to check
 * @returns true if the word ends with sentence-ending punctuation
 */
function isSentenceEnd(word: string): boolean {
  const trimmed = word.trim();
  return /[.!?]$/.test(trimmed);
}

/**
 * Check if a word represents a clause boundary (comma, semicolon)
 * @param word - The word to check
 * @returns true if the word ends with clause-ending punctuation
 */
function isClauseEnd(word: string): boolean {
  const trimmed = word.trim();
  return /[,;:]$/.test(trimmed);
}

/**
 * Segment a script into 15-30 second chunks using word timings
 * Attempts to break at sentence boundaries for natural reading flow
 * 
 * @param script - The full script text
 * @param wordTimings - Array of word timing data from Script Writer agent
 * @param targetDuration - Target duration per segment in seconds (default: 25)
 * @param minDuration - Minimum duration per segment in seconds (default: 15)
 * @param maxDuration - Maximum duration per segment in seconds (default: 30)
 * @returns Array of script segments with timing information
 */
export function segmentScript(
  script: string,
  wordTimings: WordTiming[],
  targetDuration: number = 25,
  minDuration: number = 15,
  maxDuration: number = 30
): ScriptSegment[] {
  // Handle edge cases - missing or invalid inputs
  if (!script || typeof script !== 'string' || script.trim().length === 0) {
    console.warn('scriptSegmentation: Invalid script provided');
    return [];
  }

  if (!wordTimings || !Array.isArray(wordTimings) || wordTimings.length === 0) {
    console.warn('scriptSegmentation: Missing word timings, using fallback segmentation');
    return fallbackSegmentation(script, targetDuration);
  }

  // Validate word timings structure
  const hasValidTimings = wordTimings.every(
    timing => timing && 
    typeof timing.word === 'string' && 
    typeof timing.start === 'number' && 
    typeof timing.end === 'number' &&
    timing.end >= timing.start
  );

  if (!hasValidTimings) {
    console.warn('scriptSegmentation: Invalid word timing structure, using fallback');
    return fallbackSegmentation(script, targetDuration);
  }

  const segments: ScriptSegment[] = [];
  let currentSegment = '';
  let currentWords: WordTiming[] = [];
  let startTime = 0;

  for (let i = 0; i < wordTimings.length; i++) {
    const timing = wordTimings[i];
    currentWords.push(timing);
    currentSegment += timing.word + ' ';
    
    const currentDuration = timing.end - startTime;
    const isLastWord = i === wordTimings.length - 1;

    // Determine if we should split here
    let shouldSplit = false;

    if (isLastWord) {
      // Always include the last word
      shouldSplit = true;
    } else if (currentDuration >= maxDuration) {
      // Exceeded max duration - split at next boundary
      if (isSentenceEnd(timing.word)) {
        shouldSplit = true;
      } else if (isClauseEnd(timing.word) && currentDuration >= maxDuration + 2) {
        // If we're way over, split at clause
        shouldSplit = true;
      }
    } else if (currentDuration >= targetDuration && currentDuration <= maxDuration) {
      // In target range - split at sentence boundary
      if (isSentenceEnd(timing.word)) {
        shouldSplit = true;
      }
    } else if (currentDuration >= minDuration && currentDuration < targetDuration) {
      // Above minimum - only split at strong sentence boundaries
      if (isSentenceEnd(timing.word) && /[.!?]$/.test(timing.word)) {
        // Look ahead to see if next segment would be too short
        const remainingDuration = wordTimings[wordTimings.length - 1].end - timing.end;
        if (remainingDuration >= minDuration || isLastWord) {
          shouldSplit = true;
        }
      }
    }

    if (shouldSplit && currentWords.length > 0) {
      segments.push({
        text: currentSegment.trim(),
        duration: currentDuration,
        startTime: startTime,
        endTime: timing.end
      });

      // Reset for next segment
      currentSegment = '';
      currentWords = [];
      startTime = timing.end;
    }
  }

  // Add any remaining segment (shouldn't happen with isLastWord logic, but safety check)
  if (currentSegment.trim() && currentWords.length > 0) {
    const lastTiming = currentWords[currentWords.length - 1];
    segments.push({
      text: currentSegment.trim(),
      duration: lastTiming.end - startTime,
      startTime: startTime,
      endTime: lastTiming.end
    });
  }

  return segments;
}

/**
 * Fallback segmentation when word timings are unavailable
 * Splits script by sentences and estimates duration based on word count
 * 
 * @param script - The full script text
 * @param targetDuration - Target duration per segment in seconds
 * @returns Array of script segments with estimated timing
 */
export function fallbackSegmentation(
  script: string,
  targetDuration: number = 20
): ScriptSegment[] {
  // Handle empty or invalid script
  if (!script || typeof script !== 'string' || script.trim().length === 0) {
    console.warn('scriptSegmentation: Empty or invalid script provided');
    return [];
  }

  // Split by sentence boundaries
  const sentences = script.match(/[^.!?]+[.!?]+/g);
  
  // If no sentence boundaries found, treat entire script as one segment
  if (!sentences || sentences.length === 0) {
    console.warn('scriptSegmentation: No sentence boundaries found, using entire script');
    const wordCount = script.trim().split(/\s+/).length;
    const duration = Math.max(15, Math.min(30, wordCount / 2.5));
    
    return [{
      text: script.trim(),
      duration: duration,
      startTime: 0,
      endTime: duration
    }];
  }
  
  // Average speaking rate: ~150 words per minute = 2.5 words per second
  const wordsPerSecond = 2.5;
  
  const segments: ScriptSegment[] = [];
  let currentSegment = '';
  let currentStartTime = 0;
  let currentDuration = 0;

  for (let i = 0; i < sentences.length; i++) {
    const sentence = sentences[i].trim();
    
    // Skip empty sentences
    if (!sentence) {
      continue;
    }
    
    const wordCount = sentence.split(/\s+/).filter(w => w.length > 0).length;
    const sentenceDuration = Math.max(2, wordCount / wordsPerSecond); // Minimum 2 seconds per sentence

    if (currentDuration + sentenceDuration <= targetDuration || currentSegment === '') {
      // Add to current segment
      currentSegment += sentence + ' ';
      currentDuration += sentenceDuration;
    } else {
      // Save current segment and start new one
      segments.push({
        text: currentSegment.trim(),
        duration: Math.max(15, currentDuration), // Ensure minimum 15 seconds
        startTime: currentStartTime,
        endTime: currentStartTime + currentDuration
      });

      currentSegment = sentence + ' ';
      currentStartTime += currentDuration;
      currentDuration = sentenceDuration;
    }

    // Handle last sentence
    if (i === sentences.length - 1 && currentSegment.trim()) {
      segments.push({
        text: currentSegment.trim(),
        duration: Math.max(15, currentDuration), // Ensure minimum 15 seconds
        startTime: currentStartTime,
        endTime: currentStartTime + currentDuration
      });
    }
  }

  // Fallback: if no segments created, create one from entire script
  if (segments.length === 0) {
    console.warn('scriptSegmentation: No segments created, using entire script as single segment');
    const wordCount = script.trim().split(/\s+/).length;
    const duration = Math.max(15, Math.min(30, wordCount / 2.5));
    
    segments.push({
      text: script.trim(),
      duration: duration,
      startTime: 0,
      endTime: duration
    });
  }

  return segments;
}

/**
 * Generate segments from news item summaries when script is unavailable
 * Creates one segment per news item with estimated duration
 * 
 * @param newsItems - Array of news items with title and summary
 * @param defaultDuration - Default duration per segment in seconds
 * @returns Array of script segments
 */
export function generateSegmentsFromSummaries(
  newsItems: Array<{ title: string; summary: string }>,
  defaultDuration: number = 20
): ScriptSegment[] {
  if (!newsItems || !Array.isArray(newsItems) || newsItems.length === 0) {
    console.warn('scriptSegmentation: No news items provided for summary generation');
    return [];
  }

  const segments: ScriptSegment[] = [];
  let currentTime = 0;

  newsItems.forEach((item, index) => {
    // Combine title and summary
    const text = `${item.title}. ${item.summary}`.trim();
    
    // Skip empty items
    if (!text || text.length === 0) {
      console.warn(`scriptSegmentation: Empty news item at index ${index}`);
      return;
    }

    // Estimate duration based on word count
    const wordCount = text.split(/\s+/).filter(w => w.length > 0).length;
    const estimatedDuration = Math.max(15, Math.min(30, wordCount / 2.5));

    segments.push({
      text: text,
      duration: estimatedDuration,
      startTime: currentTime,
      endTime: currentTime + estimatedDuration
    });

    currentTime += estimatedDuration;
  });

  return segments;
}

/**
 * Calculate total duration from word timings
 * @param wordTimings - Array of word timing data
 * @returns Total duration in seconds
 */
export function calculateTotalDuration(wordTimings: WordTiming[]): number {
  if (!wordTimings || wordTimings.length === 0) {
    return 0;
  }
  return wordTimings[wordTimings.length - 1].end;
}

/**
 * Validate script segments for quality
 * Ensures segments meet duration requirements and have content
 * 
 * @param segments - Array of script segments to validate
 * @param minDuration - Minimum acceptable duration
 * @param maxDuration - Maximum acceptable duration
 * @returns Validation result with any issues found
 */
export function validateSegments(
  segments: ScriptSegment[],
  minDuration: number = 15,
  maxDuration: number = 30
): { valid: boolean; issues: string[] } {
  const issues: string[] = [];

  if (segments.length === 0) {
    issues.push('No segments generated');
    return { valid: false, issues };
  }

  segments.forEach((segment, index) => {
    if (!segment.text || segment.text.trim().length === 0) {
      issues.push(`Segment ${index + 1}: Empty text`);
    }

    if (segment.duration < minDuration) {
      issues.push(`Segment ${index + 1}: Duration ${segment.duration.toFixed(1)}s below minimum ${minDuration}s`);
    }

    if (segment.duration > maxDuration) {
      issues.push(`Segment ${index + 1}: Duration ${segment.duration.toFixed(1)}s exceeds maximum ${maxDuration}s`);
    }

    if (segment.startTime < 0 || segment.endTime < 0) {
      issues.push(`Segment ${index + 1}: Invalid timing (negative values)`);
    }

    if (segment.endTime <= segment.startTime) {
      issues.push(`Segment ${index + 1}: End time must be after start time`);
    }
  });

  return {
    valid: issues.length === 0,
    issues
  };
}
