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

const InteractiveTranscript: React.FC<InteractiveTranscriptProps> = ({
  script,
  wordTimings,
  currentTime
}) => {
  const [currentWordIndex, setCurrentWordIndex] = useState<number>(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const transcriptRef = useRef<HTMLDivElement>(null);
  const wordsRef = useRef<(HTMLSpanElement | null)[]>([]);

  // Split script into words and create mock timings if none provided
  const words = script ? script.split(/\s+/).filter(word => word.length > 0) : [];
  
  // Generate mock word timings if not provided (for demo purposes)
  const mockWordTimings: WordTiming[] = words.map((word, index) => {
    // More realistic timing based on word length
    const baseTime = index * 0.4; // Base 0.4 seconds per word
    const wordLength = word.length;
    const duration = Math.max(0.2, Math.min(0.8, wordLength * 0.05)); // 0.2-0.8 seconds based on length
    
    return {
      word: word.replace(/[^\w]/g, ''), // Remove punctuation for matching
      start: baseTime,
      end: baseTime + duration
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

    // Find the current word based on timing with better precision
    let wordIndex = -1;
    
    // First try exact timing match
    for (let i = 0; i < effectiveTimings.length; i++) {
      const timing = effectiveTimings[i];
      if (currentTime >= timing.start && currentTime <= timing.end) {
        wordIndex = i;
        break;
      }
    }
    
    // If no exact match, find the closest word
    if (wordIndex === -1) {
      let closestDistance = Infinity;
      for (let i = 0; i < effectiveTimings.length; i++) {
        const timing = effectiveTimings[i];
        const distance = Math.abs(currentTime - timing.start);
        if (distance < closestDistance && currentTime >= timing.start - 0.1) {
          closestDistance = distance;
          wordIndex = i;
        }
      }
    }
    
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

  // Show loading state if no script is available
  if (!script) {
    return (
      <div className="transcript-section">
        <h2>📝 Interactive Transcript</h2>
        <div className="transcript-loading">
          <p>Loading transcript...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="transcript-section">
      <h2>📝 Interactive Transcript</h2>
      <div className="transcript-instructions">
        Click any word to jump to that point in the audio
      </div>
      
      <div className="transcript-stats">
        <span>Words: {words.length}</span>
        {wordTimings.length > 0 && (
          <span>Timings: {wordTimings.length}</span>
        )}
        {currentTime > 0 && (
          <span>Time: {currentTime.toFixed(1)}s</span>
        )}
      </div>
      
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