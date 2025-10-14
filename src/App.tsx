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
  const audioRef = useRef<HTMLAudioElement>(null);

  const fetchNews = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'https://q4qn6e5kd2ffgdawnqaqs7en2y0suukd.lambda-url.us-west-2.on.aws/';
      
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }
      
      const data: NewsData = await response.json();
      setNewsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch news');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

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
          <div className="news-section">
            {/* Interactive Transcript */}
            <div className="transcript-section">
              <h2>📝 Interactive Transcript</h2>
              <div className="transcript-container">
                <div className="transcript-text">
                  {newsData.script.split(' ').map((word, index) => (
                    <span
                      key={index}
                      className={`transcript-word ${
                        Math.floor(currentTime * 2) === index ? 'highlighted' : ''
                      }`}
                      onClick={() => {
                        if (audioRef.current) {
                          audioRef.current.currentTime = index * 0.5;
                        }
                      }}
                    >
                      {word}{' '}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* News Cards */}
            <div className="news-cards">
              {newsData.news_items.map((item, index) => (
                <div 
                  key={index} 
                  className="news-card"
                  onClick={() => {
                    // Simple modal or expand functionality
                    alert(`Full Story:\n\n${item.title}\n\n${item.full_text}`);
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
                    <p className="news-summary">{item.summary}</p>
                    <div className="read-more">Tap to read more →</div>
                  </div>
                </div>
              ))}
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
                if (audioRef.current) {
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
              setError('Audio failed to load. Please try refreshing.');
            }}
          />
        </div>
      )}
    </div>
  );
};

export default App;