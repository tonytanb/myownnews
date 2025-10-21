import React from 'react';
import './WeekendRecommendations.css';

interface Book {
  title: string;
  author: string;
  description: string;
  genre: string;
}

interface Movie {
  title: string;
  platform: string;
  description: string;
  genre: string;
}

interface Event {
  name: string;
  location: string;
  date: string;
  description: string;
  link?: string;
}

interface WeekendData {
  books?: Book[];
  movies?: Movie[];
  events?: Event[];
  cultural_insights?: {
    BookTok_trends?: string;
    streaming_releases?: string;
    social_media_phenomena?: string;
  };
  description?: string;
}

interface WeekendRecommendationsProps {
  weekendData?: WeekendData;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  retryAttempt?: number;
  maxRetries?: number;
}

const WeekendRecommendations: React.FC<WeekendRecommendationsProps> = ({ 
  weekendData, 
  isLoading, 
  error, 
  onRetry, 
  retryAttempt = 0, 
  maxRetries = 3 
}) => {
  // Show error state
  if (error) {
    const canRetry = onRetry && retryAttempt < maxRetries;
    const isMaxRetries = retryAttempt >= maxRetries;
    
    return (
      <div className="weekend-section">
        <div className="weekend-header">
          <h3>🎉 Weekend Recommendations</h3>
          <span className="error-badge">Failed</span>
        </div>
        <div className="weekend-error">
          <div className="error-icon">❌</div>
          <div className="error-details">
            <h4>Content Generation Failed</h4>
            <p className="error-message">{error}</p>
            
            {retryAttempt > 0 && (
              <p className="retry-info">
                Retry attempt {retryAttempt}/{maxRetries} failed.
              </p>
            )}
            
            {isMaxRetries ? (
              <div className="max-retries-reached">
                <p>⚠️ Maximum retry attempts reached.</p>
                <p>The Weekend Events Agent may be experiencing technical difficulties.</p>
                <p>💡 <strong>Fallback:</strong> Check out local event websites or social media for weekend activities!</p>
              </div>
            ) : (
              <div className="error-help">
                <p>🤖 Our Weekend Events Agent encountered an issue while curating recommendations.</p>
                <p>This could be due to high demand or temporary service issues.</p>
              </div>
            )}
          </div>
          
          <div className="error-actions">
            {canRetry && (
              <button 
                className="retry-button primary"
                onClick={onRetry}
              >
                🔄 Retry Weekend Recommendations ({maxRetries - retryAttempt} attempts left)
              </button>
            )}
            <button 
              className="retry-button secondary"
              onClick={() => window.location.reload()}
            >
              🔄 Refresh Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show loading state
  if (isLoading || !weekendData) {
    return (
      <div className="weekend-section">
        <h3>🎉 Weekend Recommendations</h3>
        <div className="weekend-placeholder">
          <div className="loading-spinner">⏳</div>
          <p>🤖 Our Weekend Events Agent is curating the perfect recommendations for you...</p>
          <div className="loading-progress">
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
            <p className="progress-text">Analyzing trending books, movies, and local events...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="weekend-section">
      <div className="weekend-header">
        <h3>🎉 Weekend Recommendations</h3>
        <span className="weekend-badge">AI Curated</span>
      </div>

      <div className="weekend-grid">
        {/* Books Section */}
        {weekendData.books && weekendData.books.length > 0 && (
          <div className="recommendation-category">
            <h4>📚 BookTok Trending</h4>
            <div className="books-grid">
              {weekendData.books.map((book, index) => (
                <div key={index} className="book-card">
                  <div className="book-genre">{book.genre}</div>
                  <h5 className="book-title">{book.title}</h5>
                  <p className="book-author">by {book.author}</p>
                  <p className="book-description">{book.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Movies Section */}
        {weekendData.movies && weekendData.movies.length > 0 && (
          <div className="recommendation-category">
            <h4>🎬 Streaming Picks</h4>
            <div className="movies-grid">
              {weekendData.movies.map((movie, index) => (
                <div key={index} className="movie-card">
                  <div className="movie-platform">{movie.platform}</div>
                  <h5 className="movie-title">{movie.title}</h5>
                  <p className="movie-genre">{movie.genre}</p>
                  <p className="movie-description">{movie.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Events Section */}
        {weekendData.events && weekendData.events.length > 0 && (
          <div className="recommendation-category">
            <h4>🎪 Local Events</h4>
            <div className="events-grid">
              {weekendData.events.map((event, index) => (
                <div key={index} className="event-card">
                  <h5 className="event-name">{event.name}</h5>
                  <p className="event-location">📍 {event.location}</p>
                  <p className="event-date">📅 {event.date}</p>
                  <p className="event-description">{event.description}</p>
                  {event.link && (
                    <a 
                      href={event.link} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="event-link"
                    >
                      🔗 Find Events
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Cultural Insights */}
      {weekendData.cultural_insights && (
        <div className="cultural-insights">
          <h4>🔥 Cultural Pulse</h4>
          <div className="insights-grid">
            {weekendData.cultural_insights.BookTok_trends && (
              <div className="insight-item">
                <h5>📖 BookTok Trends</h5>
                <p>{weekendData.cultural_insights.BookTok_trends}</p>
              </div>
            )}
            {weekendData.cultural_insights.streaming_releases && (
              <div className="insight-item">
                <h5>📺 Streaming Buzz</h5>
                <p>{weekendData.cultural_insights.streaming_releases}</p>
              </div>
            )}
            {weekendData.cultural_insights.social_media_phenomena && (
              <div className="insight-item">
                <h5>📱 Social Media</h5>
                <p>{weekendData.cultural_insights.social_media_phenomena}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Fallback description */}
      {weekendData.description && !weekendData.books && !weekendData.movies && !weekendData.events && (
        <div className="weekend-description">
          <p>{weekendData.description}</p>
        </div>
      )}

      <div className="agent-credit">
        <span className="agent-emoji">🎉</span>
        <span className="agent-text">Curated by our Weekend Events Agent</span>
      </div>
    </div>
  );
};

export default WeekendRecommendations;