import React, { useState, useEffect, useRef } from 'react';
import './InteractiveTranscript.css';

interface WordTiming {
  word: string;
  start: number;
  end: number;
}

interface InteractiveTranscriptProps {
  script: string;
  wordTimings: WordTiming[];
  currentTime: number;
}

/**
 * Clean script by removing stage directions, prompt text, and meta-instructions
 */
function cleanScript(rawScript: string): string {
  if (!rawScript) return '';
  
  let cleaned = rawScript;
  
  // Remove stage directions in asterisks: *like this*
  cleaned = cleaned.replace(/\*[^*]+\*/g, '');
  
  // Remove common prompt phrases at the start
  cleaned = cleaned.replace(/^(Hey fam,?|Welcome back to|Hi everyone,?|Good morning,?|Good evening,?)\s*/i, '');
  
  // Remove meta-instructions in brackets
  cleaned = cleaned.replace(/\[[^\]]+\]/g, '');
  
  // Remove parenthetical stage directions
  cleaned = cleaned.replace(/\([^)]*tone[^)]*\)/gi, '');
  cleaned = cleaned.replace(/\([^)]*pause[^)]*\)/gi, '');
  
  // Normalize whitespace
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  
  return cleaned;
}

const InteractiveTranscript: React.FC<InteractiveTranscriptProps> = ({
  script,
  wordTimings,
  currentTime
}) => {
  // Clean the script before processing
  const cleanedScript = cleanScript(script);
  const [currentWordIndex, setCurrentWordIndex] = useState<number>(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const transcriptRef = useRef<HTMLDivElement>(null);
  const wordsRef = useRef<(HTMLSpanElement | null)[]>([]);

  // Split cleaned script into words and create mock timings if none provided
  const words = cleanedScript ? cleanedScript.split(/\s+/).filter(word => word.length > 0) : [];
  
  // Generate mock word timings if not provided (for demo purposes)
  const mockWordTimings: WordTiming[] = words.map((word, index) => {
    // More realistic timing based on word length and natural speech patterns
    let cumulativeTime = 0;
    
    // Calculate cumulative time based on previous words
    for (let i = 0; i < index; i++) {
      const prevWord = words[i];
      const prevWordLength = prevWord.length;
      // Average speaking rate: 150-160 words per minute = ~0.4 seconds per word
      // Adjust for word length and add natural pauses
      const wordDuration = Math.max(0.25, Math.min(0.7, prevWordLength * 0.06 + 0.2));
      const pause = prevWord.endsWith('.') || prevWord.endsWith('!') || prevWord.endsWith('?') ? 0.3 : 0.1;
      cumulativeTime += wordDuration + pause;
    }
    
    const wordLength = word.length;
    const duration = Math.max(0.25, Math.min(0.7, wordLength * 0.06 + 0.2));
    
    return {
      word: word.replace(/[^\w]/g, ''), // Remove punctuation for matching
      start: cumulativeTime,
      end: cumulativeTime + duration
    };
  });

  const effectiveTimings = wordTimings.length > 0 ? wordTimings : mockWordTimings;

  // Listen for audio events
  useEffect(() => {
    const handleAudioPlay = () => setIsPlaying(true);
    const handleAudioPause = () => setIsPlaying(false);
    const handleAudioEnd = () => {
      setIsPlaying(false);
      setCurrentWordIndex(-1);
    };

    window.addEventListener('audio-play', handleAudioPlay);
    window.addEventListener('audio-pause', handleAudioPause);
    window.addEventListener('audio-end', handleAudioEnd);

    return () => {
      window.removeEventListener('audio-play', handleAudioPlay);
      window.removeEventListener('audio-pause', handleAudioPause);
      window.removeEventListener('audio-end', handleAudioEnd);
    };
  }, []);

  useEffect(() => {
    if (!isPlaying || currentTime <= 0) return;

    // Speed up timings by 25% to match faster audio playback
    const SPEED_MULTIPLIER = 0.75; // 0.75 = 25% faster (divide time by 1.25)
    const adjustedTime = currentTime * SPEED_MULTIPLIER;

    // Find the current word based on timing - improved algorithm
    let wordIndex = -1;
    
    // Use a more progressive approach - find the latest word that should have started
    for (let i = effectiveTimings.length - 1; i >= 0; i--) {
      const timing = effectiveTimings[i];
      if (adjustedTime >= timing.start) {
        // Check if we're still within a reasonable range of this word
        const timeSinceStart = adjustedTime - timing.start;
        const expectedDuration = timing.end - timing.start;
        
        // Allow some flexibility - word can be highlighted a bit longer than its exact timing
        if (timeSinceStart <= expectedDuration + 0.3) {
          wordIndex = i;
          break;
        }
      }
    }
    
    // Fallback: if no word found, find the closest upcoming word
    if (wordIndex === -1) {
      for (let i = 0; i < effectiveTimings.length; i++) {
        const timing = effectiveTimings[i];
        if (timing.start > adjustedTime) {
          // If we're very close to the next word (within 0.2s), highlight it
          if (timing.start - adjustedTime <= 0.2) {
            wordIndex = i;
          }
          break;
        }
      }
    }
    
    // Only update if we have a valid word and it's different from current
    if (wordIndex !== -1 && wordIndex !== currentWordIndex) {
      setCurrentWordIndex(wordIndex);
      
      // Auto-scroll to keep highlighted word visible
      const wordElement = wordsRef.current[wordIndex];
      if (wordElement && transcriptRef.current) {
        const transcriptRect = transcriptRef.current.getBoundingClientRect();
        const wordRect = wordElement.getBoundingClientRect();
        
        // Check if word is outside visible area
        if (wordRect.top < transcriptRect.top || wordRect.bottom > transcriptRect.bottom) {
          wordElement.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
        }
      }
    }
    
    // Clear highlighting if we're past all words
    if (adjustedTime > effectiveTimings[effectiveTimings.length - 1]?.end + 1) {
      setCurrentWordIndex(-1);
    }
  }, [currentTime, currentWordIndex, effectiveTimings, isPlaying]);

  const handleWordClick = (wordIndex: number) => {
    setCurrentWordIndex(wordIndex);
    
    // Trigger audio seeking if timing data is available
    const timing = effectiveTimings[wordIndex];
    if (timing && timing.start >= 0) {
      // Dispatch custom event for audio seeking
      const seekEvent = new CustomEvent('transcript-seek', {
        detail: { time: timing.start }
      });
      window.dispatchEvent(seekEvent);
    }
  };

  // Show empty state if no script is available
  if (!cleanedScript) {
    return (
      <div className="transcript-section">
        <div className="transcript-loading">
          <p>Transcript will appear here once audio is generated</p>
        </div>
      </div>
    );
  }

  return (
    <div className="transcript-section">
      <div 
        ref={transcriptRef}
        className="transcript-container"
      >
        <div className="transcript-text">
          {words.map((word, index) => (
            <span
              key={index}
              ref={el => wordsRef.current[index] = el}
              className={`transcript-word ${
                index === currentWordIndex ? 'highlighted' : ''
              } ${isPlaying ? 'playable' : ''}`}
              onClick={() => handleWordClick(index)}
              title={`Jump to ${effectiveTimings[index]?.start.toFixed(1)}s`}
            >
              {word}
            </span>
          ))}
        </div>
      </div>
      
      {currentTime > 0 && (
        <div className="playback-indicator">
          🎵 Playing - words will highlight as they're spoken
        </div>
      )}
    </div>
  );
};

export default InteractiveTranscript;