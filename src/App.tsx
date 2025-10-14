import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface NewsItem {
  title: string;
  category: string;
  summary: string;
  full_text: string;
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
          
          {!newsData && !loading && (
            <button 
              onClick={fetchNews} 
              className="generate-btn"
            >
              Generate Today's Brief
            </button>
          )}
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
            {/* News Cards */}
            <div className="news-cards">
              {newsData.news_items.map((item, index) => (
                <div key={index} className="news-card">
                  <div className="news-image">
                    <div className="placeholder-image"></div>
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
            <div className="brief-title">📻 Today's Brief</div>
            <div className="audio-time">0:00</div>
          </div>
          
          <div className="audio-controls">
            <button className="control-btn">⏮️</button>
            <button className="control-btn">⏯️</button>
            <button className="control-btn">⏭️</button>
            <button className="control-btn">🔄</button>
            <div className="volume-control">
              <button className="control-btn">🔊</button>
              <div className="volume-slider"></div>
            </div>
          </div>

          <audio 
            ref={audioRef}
            src={newsData.audio_url}
            onError={(e) => console.error('❌ Audio error:', e)}
            onLoadStart={() => console.log('🎵 Audio loading started')}
            onCanPlay={() => console.log('✅ Audio can play')}
            onLoadedData={() => console.log('✅ Audio data loaded')}
          />
        </div>
      )}
    </div>
  );
};

export default App;