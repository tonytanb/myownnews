import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import InteractiveTranscript from './components/InteractiveTranscript';
import NewsItems from './components/NewsItems';

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
      const response = await fetch(apiUrl);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
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
      <header className="app-header">
        <h1>🎙️ Curio News</h1>
        <p>AI-powered international news with interactive transcripts</p>
        <button 
          onClick={fetchNews} 
          disabled={loading}
          className="refresh-button"
        >
          {loading ? '🔄 Generating...' : '🔄 Generate Fresh News'}
        </button>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-message">
            ❌ Error: {error}
          </div>
        )}

        {loading && (
          <div className="loading-message">
            <div className="loading-spinner"></div>
            <p>Generating your personalized news briefing...</p>
          </div>
        )}

        {newsData && (
          <div className="news-content">
            <div className="audio-section">
              <h2>🎧 Audio Briefing</h2>
              <audio 
                ref={audioRef}
                controls 
                src={newsData.audio_url}
                className="audio-player"
              >
                Your browser does not support the audio element.
              </audio>
              <p className="generated-time">
                Generated: {new Date(newsData.generated_at).toLocaleString()}
              </p>
            </div>

            <InteractiveTranscript 
              script={newsData.script}
              wordTimings={newsData.word_timings}
              audioRef={audioRef}
            />

            <NewsItems items={newsData.news_items} />
          </div>
        )}
      </main>
    </div>
  );
};

export default App;