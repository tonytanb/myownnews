import React from 'react';
import './WeekendRecommendations.css';
import MovieCard from './MovieCard';
import SeriesCard from './SeriesCard';
import PlayCard from './PlayCard';

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

// New entertainment recommendation interfaces
export interface TopMovie {
  title: string;
  genre: string;
  rating: string; // e.g., "8.5/10", "95% RT"
  platform: string; // Netflix, Prime Video, etc.
  description: string;
  release_year?: number;
  runtime?: string; // e.g., "2h 15m"
  image?: string;
}

export interface TVSeries {
  title: string;
  genre: string;
  rating: string;
  platform: string;
  description: string;
  seasons: number;
  episodes_per_season?: number;
  status: 'ongoing' | 'completed' | 'new_season';
  image?: string;
}

export interface TheaterPlay {
  title: string;
  genre: string;
  venue?: string;
  city?: string;
  description: string;
  show_times?: string;
  ticket_info?: string;
  rating?: string;
  image?: string;
}

export interface MusicRelease {
  title: string;
  artist: string;
  genre: string;
  platform: string;
  description: string;
  release_date: string;
  rating: string;
  link?: string;
  stream_link?: string;
  image?: string;
}

export interface EntertainmentRecommendations {
  top_movies?: TopMovie[];
  must_watch_series?: TVSeries[];
  theater_plays?: TheaterPlay[];
  new_music?: MusicRelease[];
}

export interface WeekendData {
  books?: Book[];
  movies?: Movie[];
  events?: Event[];
  entertainment_recommendations?: EntertainmentRecommendations;
  // Deprecated: keeping for backward compatibility
  /** @deprecated Use entertainment_recommendations instead */
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
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <p>curating your weekend vibe</p>
          <div className="loading-progress">
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
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

      </div>

      {/* Entertainment Hub */}
      {weekendData.entertainment_recommendations && 
       ((weekendData.entertainment_recommendations.top_movies?.length ?? 0) > 0 ||
        (weekendData.entertainment_recommendations.must_watch_series?.length ?? 0) > 0 ||
        (weekendData.entertainment_recommendations.theater_plays?.length ?? 0) > 0 ||
        (weekendData.entertainment_recommendations.new_music?.length ?? 0) > 0) && (
        <div className="entertainment-hub">
          <h4>🎬 Entertainment Hub</h4>
          <div className="entertainment-categories">
            {/* Top Movies */}
            {weekendData.entertainment_recommendations.top_movies && 
             weekendData.entertainment_recommendations.top_movies.length > 0 && (
              <div className="entertainment-category">
                <h5>🍿 Top Movies</h5>
                <div className="entertainment-grid">
                  {weekendData.entertainment_recommendations.top_movies.map((movie, index) => (
                    <MovieCard key={index} movie={movie} />
                  ))}
                </div>
              </div>
            )}
            
            {/* Must-Watch Series */}
            {weekendData.entertainment_recommendations.must_watch_series && 
             weekendData.entertainment_recommendations.must_watch_series.length > 0 && (
              <div className="entertainment-category">
                <h5>📺 Must-Watch Series</h5>
                <div className="entertainment-grid">
                  {weekendData.entertainment_recommendations.must_watch_series.map((series, index) => (
                    <SeriesCard key={index} series={series} />
                  ))}
                </div>
              </div>
            )}
            
            {/* Theater & Plays */}
            {weekendData.entertainment_recommendations.theater_plays && 
             weekendData.entertainment_recommendations.theater_plays.length > 0 && (
              <div className="entertainment-category">
                <h5>🎭 Theater & Plays</h5>
                <div className="entertainment-grid">
                  {weekendData.entertainment_recommendations.theater_plays.map((play, index) => (
                    <PlayCard key={index} play={play} />
                  ))}
                </div>
              </div>
            )}

            {/* New Music Releases */}
            {weekendData.entertainment_recommendations.new_music && 
             weekendData.entertainment_recommendations.new_music.length > 0 && (
              <div className="entertainment-category">
                <h5>🎵 New Music Releases</h5>
                <div className="entertainment-grid">
                  {weekendData.entertainment_recommendations.new_music.map((music, index) => (
                    <a 
                      key={index} 
                      href={music.link || music.stream_link || '#'} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="entertainment-card music-card"
                      style={{ textDecoration: 'none', color: 'inherit', cursor: 'pointer' }}
                    >
                      {music.image && (
                        <div className="card-image" style={{ 
                          backgroundImage: `url(${music.image})`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                          height: '180px',
                          borderRadius: '8px 8px 0 0',
                          marginBottom: '12px'
                        }} />
                      )}
                      <div className="card-header">
                        <div className="platform-badge">{music.platform}</div>
                        <div className="rating-badge">{music.rating}</div>
                      </div>
                      <h6 className="entertainment-title">{music.title}</h6>
                      <div className="entertainment-meta">
                        <span className="artist">🎤 {music.artist}</span>
                        <span className="genre">{music.genre}</span>
                        <span className="release-date">{music.release_date}</span>
                      </div>
                      <p className="entertainment-description">{music.description}</p>
                      <div className="external-link-indicator">
                        <span>{music.link ? 'Visit Artist Site →' : 'Listen Now →'}</span>
                      </div>
                    </a>
                  ))}
                </div>
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