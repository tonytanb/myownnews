import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface NewsItem {
  title: string;
  category: string;
  summary: string;
  full_text: string;
  image: string;
}

interface NewsData {
  script: string;
  audio_url: string;
  word_timings: Array<{ word: string; start: number; end: number }>;
  news_items: NewsItem[];
  generated_at: string;
}

const App: React.FC = () => {
  const [newsData, setNewsData] = useState<NewsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [expandedCard, setExpandedCard] = useState<number | null>(null);
  const [usingSpeechSynthesis, setUsingSpeechSynthesis] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const transcriptRef = useRef<HTMLDivElement>(null);
  const wordsRef = useRef<(HTMLSpanElement | null)[]>([]);
  const speechRef = useRef<SpeechSynthesisUtterance | null>(null);

  const fetchNews = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Try real API first, fallback to mock data
      const apiUrl = process.env.REACT_APP_API_URL || 'https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod/latest';
      
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: NewsData = await response.json();
      setNewsData(data);
    } catch (err) {
      console.log('API failed, using mock data for demo');
      // Mock data for demo
      const mockData: NewsData = {
        script: "Alright, let's dive into what's happening around the world today. We've got some wild stories to cover, so let's get started. First up, the biggest news from North Carolina where Republicans are planning to vote on redrawing the state's House district map. This is part of a nationwide redistricting battle that's getting pretty intense. Moving to international news, there's been significant developments in the Middle East with new ceasefire negotiations. The situation remains complex but there's cautious optimism. In technology news, Microsoft has announced their first in-house image generator, marking a major step in the AI competition. And finally, cybersecurity experts are warning about new Android vulnerabilities that could affect millions of users. That's your news update for today!",
        audio_url: "", // We'll use Web Speech API for demo
        word_timings: [],
        news_items: [
          {
            title: "North Carolina Republicans plan vote on new House map amid nationwide redistricting battle",
            category: "POLITICS",
            summary: "Republican legislative leaders announced plans to vote next week on redrawing the state's US House district map, with a likely aim to secure another GOP seat.",
            full_text: "North Carolina Republican legislative leaders announced plans Monday to vote next week on redrawing the state's US House district map, with a likely aim to secure another GOP seat within already right-leaning boundaries. The plan comes amid an emerging nationwide redistricting battle.",
            image: "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=400"
          },
          {
            title: "Microsoft AI announces first image generator created in-house",
            category: "TECHNOLOGY", 
            summary: "Microsoft AI announced a new text-to-image generator developed in-house, marking their entry into the competitive AI image generation market.",
            full_text: "Microsoft AI has unveiled their first proprietary text-to-image generator, developed entirely in-house. This represents a significant milestone in Microsoft's AI strategy and positions them to compete directly with other major players in the generative AI space.",
            image: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400"
          },
          {
            title: "Hackers can steal 2FA codes and private messages from Android phones",
            category: "CYBERSECURITY",
            summary: "Security researchers have discovered a new vulnerability that allows malicious apps to steal two-factor authentication codes and private messages.",
            full_text: "Cybersecurity experts have identified a critical vulnerability in Android devices that enables malicious applications to intercept two-factor authentication codes and private messages. The attack, dubbed 'Pixnapping,' requires no special permissions to execute.",
            image: "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400"
          }
        ],
        generated_at: new Date().toISOString()
      };
      // Check if we need to use Web Speech API
      if (!mockData.audio_url && 'speechSynthesis' in window) {
        setUsingSpeechSynthesis(true);
        setDuration(mockData.script.split(' ').length * 0.4); // Estimate duration
      }
      
      setNewsData(mockData);
    } finally {
      setLoading(false);
    }
  };

  // Speech synthesis functions
  const startSpeechSynthesis = () => {
    if (!newsData || !usingSpeechSynthesis) return;
    
    if (speechRef.current) {
      speechSynthesis.cancel();
    }
    
    const utterance = new SpeechSynthesisUtterance(newsData.script);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = isMuted ? 0 : volume;
    
    // Try to get a good voice
    const voices = speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice => 
      voice.name.includes('Google') || 
      voice.name.includes('Microsoft') ||
      (voice.lang.startsWith('en') && voice.name.includes('US'))
    ) || voices.find(voice => voice.lang.startsWith('en'));
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }
    
    utterance.onstart = () => {
      setIsPlaying(true);
      // Start time tracking
      const startTime = Date.now();
      const updateTime = () => {
        if (speechSynthesis.speaking) {
          const elapsed = (Date.now() - startTime) / 1000;
          setCurrentTime(elapsed);
          requestAnimationFrame(updateTime);
        }
      };
      updateTime();
    };
    
    utterance.onend = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };
    
    utterance.onerror = () => {
      setIsPlaying(false);
      setError('Speech synthesis failed. Please try refreshing.');
    };
    
    speechRef.current = utterance;
    speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    fetchNews();
  }, []);

  // Auto-scroll transcript to keep highlighted word visible
  useEffect(() => {
    if (!newsData || !transcriptRef.current) return;
    
    const words = newsData.script.split(' ');
    const currentWordIndex = Math.floor(currentTime * 2.5); // 2.5 words per second
    
    if (currentWordIndex >= 0 && currentWordIndex < words.length) {
      const wordElement = wordsRef.current[currentWordIndex];
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
  }, [currentTime, newsData]);

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="logo">CURIO</div>
        <div className="header-actions">
          <button className="menu-btn">☰</button>
          <button className="settings-btn">⚙️</button>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className="date-header">
          📅 {new Date().toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>

        <div className="title-section">
          <h1>Today's Brief</h1>
          <p className="subtitle">Your world in 5 minutes</p>
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {loading && (
          <div className="loading-section">
            <div className="loading-spinner"></div>
            <p>Curating your personalized briefing...</p>
          </div>
        )}

        {newsData && (
          <div className="content-layout">
            {/* Left Column - Transcript */}
            <div className="left-column">
              <div className="transcript-section">
                <h2>📝 Interactive Transcript</h2>
                <div className="transcript-instructions">
                  Click any word to jump to that point in the audio
                </div>
                <div className="transcript-container" ref={transcriptRef}>
                  <div className="transcript-text">
                    {newsData.script.split(' ').map((word, index) => {
                      // Calculate word timing (approximately 2.5 words per second)
                      const wordStartTime = index * 0.4;
                      const isHighlighted = currentTime >= wordStartTime && currentTime < wordStartTime + 0.4;
                      
                      return (
                        <span
                          key={index}
                          ref={el => wordsRef.current[index] = el}
                          className={`transcript-word ${isHighlighted ? 'highlighted' : ''}`}
                          onClick={() => {
                            if (audioRef.current) {
                              audioRef.current.currentTime = wordStartTime;
                            }
                          }}
                          title={`Jump to ${wordStartTime.toFixed(1)}s`}
                        >
                          {word}{' '}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column - News Cards */}
            <div className="right-column">
              <div className="news-cards-grid">
                {newsData.news_items.map((item, index) => (
                  <div 
                    key={index} 
                    className={`news-card ${expandedCard === index ? 'expanded' : ''}`}
                    onClick={() => {
                      setExpandedCard(expandedCard === index ? null : index);
                    }}
                  >
                    <div className="news-image">
                      {item.image ? (
                        <img src={item.image} alt={item.title} className="news-img" />
                      ) : (
                        <div className="placeholder-image"></div>
                      )}
                    </div>
                    <div className="news-content">
                      <div className="news-category">{item.category}</div>
                      <h3 className="news-title">{item.title}</h3>
                      <p className="news-summary">
                        {expandedCard === index ? item.full_text : item.summary}
                      </p>
                      <div className="read-more">
                        {expandedCard === index ? 'Tap to read less ↑' : 'Tap to read more →'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Bottom Audio Player */}
      {newsData && (
        <div className="audio-player-container">
          <div className="audio-info">
            <div className="brief-title">
              <span className="live-indicator">🔴 LIVE</span>
              Today's Brief
            </div>
            <div className="audio-time">
              {Math.floor(currentTime / 60)}:{String(Math.floor(currentTime % 60)).padStart(2, '0')} / {Math.floor(duration / 60)}:{String(Math.floor(duration % 60)).padStart(2, '0')}
            </div>
          </div>
          
          <div className="audio-controls">
            <button 
              className="control-btn" 
              onClick={() => {
                if (audioRef.current) {
                  audioRef.current.currentTime = Math.max(0, audioRef.current.currentTime - 15);
                }
              }}
              title="Rewind 15s"
            >
              <div className="skip-button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.5,12L20,18V6M11,18V6L2.5,12L11,18Z"/>
                </svg>
                <span className="skip-text">15</span>
              </div>
            </button>
            
            <button 
              className="play-pause-btn" 
              onClick={() => {
                if (usingSpeechSynthesis) {
                  if (isPlaying) {
                    speechSynthesis.pause();
                    setIsPlaying(false);
                  } else if (speechSynthesis.paused) {
                    speechSynthesis.resume();
                    setIsPlaying(true);
                  } else {
                    startSpeechSynthesis();
                  }
                } else if (audioRef.current) {
                  if (isPlaying) {
                    audioRef.current.pause();
                  } else {
                    audioRef.current.play().catch(e => console.error('Play failed:', e));
                  }
                }
              }}
              title={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M14,19H18V5H14M6,19H10V5H6V19Z"/>
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8,5.14V19.14L19,12.14L8,5.14Z"/>
                </svg>
              )}
            </button>
            
            <button 
              className="control-btn" 
              onClick={() => {
                if (audioRef.current) {
                  audioRef.current.currentTime = Math.min(duration, audioRef.current.currentTime + 15);
                }
              }}
              title="Forward 15s"
            >
              <div className="skip-button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M13,6V18L21.5,12M4,18L12.5,12L4,6V18Z"/>
                </svg>
                <span className="skip-text">15</span>
              </div>
            </button>
            
            <div className="volume-control">
              <button 
                className="control-btn" 
                onClick={() => {
                  if (audioRef.current) {
                    if (isMuted) {
                      audioRef.current.volume = volume;
                      setIsMuted(false);
                    } else {
                      audioRef.current.volume = 0;
                      setIsMuted(true);
                    }
                  }
                }}
                title={isMuted ? "Unmute" : "Mute"}
              >
                {isMuted || volume === 0 ? (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,4L9.91,6.09L12,8.18M4.27,3L3,4.27L7.73,9H3V15H7L12,20V13.27L16.25,17.53C15.58,18.04 14.83,18.46 14,18.7V20.77C15.38,20.45 16.63,19.82 17.68,18.96L19.73,21L21,19.73L12,10.73M19,12C19,12.94 18.8,13.82 18.46,14.64L19.97,16.15C20.62,14.91 21,13.5 21,12C21,7.72 18,4.14 14,3.23V5.29C16.89,6.15 19,8.83 19,12M16.5,12C16.5,10.23 15.5,8.71 14,7.97V10.18L16.45,12.63C16.5,12.43 16.5,12.21 16.5,12Z"/>
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.84 14,18.7V20.77C18,19.86 21,16.28 21,12C21,7.72 18,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16C15.5,15.29 16.5,13.76 16.5,12Z"/>
                  </svg>
                )}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={(e) => {
                  const newVolume = parseFloat(e.target.value);
                  setVolume(newVolume);
                  setIsMuted(newVolume === 0);
                  if (audioRef.current) {
                    audioRef.current.volume = newVolume;
                  }
                }}
                className="volume-slider"
              />
            </div>
          </div>

          {newsData.audio_url && (
            <audio 
              ref={audioRef}
              src={newsData.audio_url}
              preload="auto"
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onTimeUpdate={() => setCurrentTime(audioRef.current?.currentTime || 0)}
              onLoadedMetadata={() => {
                setDuration(audioRef.current?.duration || 0);
                if (audioRef.current) {
                  audioRef.current.volume = volume;
                }
              }}
              onCanPlay={() => console.log('✅ Audio ready to play')}
              onError={(e) => {
                console.error('❌ Audio error:', e);
                // Fallback to speech synthesis
                setUsingSpeechSynthesis(true);
                setDuration(newsData.script.split(' ').length * 0.4);
              }}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default App;