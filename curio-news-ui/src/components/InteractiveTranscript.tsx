import React, { useState, useEffect, useRef, RefObject } from 'react';
import './InteractiveTranscript.css';

interface WordTiming {
  word: string;
  start: number;
  end: number;
}

interface InteractiveTranscriptProps {
  script: string;
  wordTimings: WordTiming[];
  audioRef: RefObject<HTMLAudioElement>;
}

const InteractiveTranscript: React.FC<InteractiveTranscriptProps> = ({
  script,
  wordTimings,
  audioRef
}) => {
  const [currentWordIndex, setCurrentWordIndex] = useState<number>(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const transcriptRef = useRef<HTMLDivElement>(null);
  const wordsRef = useRef<(HTMLSpanElement | null)[]>([]);

  // Split script into words and create mock timings if none provided
  const words = script.split(/\s+/).filter(word => word.length > 0);
  
  // Generate mock word timings if not provided (for demo purposes)
  const mockWordTimings: WordTiming[] = words.map((word, index) => ({
    word: word.replace(/[^\w]/g, ''), // Remove punctuation for matching
    start: index * 0.5, // 0.5 seconds per word
    end: (index + 1) * 0.5
  }));

  const effectiveTimings = wordTimings.length > 0 ? wordTimings : mockWordTimings;

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      const currentTime = audio.currentTime;
      
      // Find the current word based on timing
      const wordIndex = effectiveTimings.findIndex(timing => 
        currentTime >= timing.start && currentTime <= timing.end
      );
      
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
    };

    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentWordIndex(-1);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [audioRef, currentWordIndex, effectiveTimings]);

  const handleWordClick = (wordIndex: number) => {
    const audio = audioRef.current;
    if (!audio) return;

    const timing = effectiveTimings[wordIndex];
    if (timing) {
      audio.currentTime = timing.start;
      if (!isPlaying) {
        audio.play();
      }
    }
  };

  return (
    <div className="transcript-section">
      <h2>📝 Interactive Transcript</h2>
      <div className="transcript-instructions">
        Click any word to jump to that point in the audio
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
      
      {isPlaying && (
        <div className="playback-indicator">
          🎵 Playing - words will highlight as they're spoken
        </div>
      )}
    </div>
  );
};

export default InteractiveTranscript;