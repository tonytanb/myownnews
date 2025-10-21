import React from 'react';
import './FavoriteStory.css';

interface FavoriteStoryProps {
  favoriteData?: {
    reasoning?: string;
    story?: {
      title: string;
      summary: string;
      category: string;
      source: string;
    };
    whyFascinating?: string;
  };
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  retryAttempt?: number;
  maxRetries?: number;
}

const FavoriteStory: React.FC<FavoriteStoryProps> = ({ 
  favoriteData, 
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
      <div className="favorite-story-section">
        <div className="favorite-header">
          <h3>⭐ Today's Favorite Story</h3>
          <span className="error-badge">Failed</span>
        </div>
        <div className="favorite-error">
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
                <p>The Favorite Selector Agent may be experiencing technical difficulties.</p>
                <p>💡 <strong>Fallback:</strong> Check the news stories above - they're still curated and ready to read!</p>
              </div>
            ) : (
              <div className="error-help">
                <p>🤖 Our Favorite Selector Agent encountered an issue while analyzing stories.</p>
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
                🔄 Retry Favorite Story ({maxRetries - retryAttempt} attempts left)
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
  if (isLoading || !favoriteData) {
    return (
      <div className="favorite-story-section">
        <h3>⭐ Today's Favorite Story</h3>
        <div className="favorite-placeholder">
          <div className="loading-spinner">⏳</div>
          <p>🤖 Our Favorite Selector Agent is analyzing stories to find the most fascinating one...</p>
          <div className="loading-progress">
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
            <p className="progress-text">Analyzing story relevance and engagement potential...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="favorite-story-section">
      <div className="favorite-header">
        <h3>⭐ Today's Favorite Story</h3>
        <span className="favorite-badge">AI Selected</span>
      </div>
      
      {favoriteData.story && (
        <div className="favorite-story-card">
          <div className="story-category">{favoriteData.story.category}</div>
          <h4 className="story-title">{favoriteData.story.title}</h4>
          <p className="story-summary">{favoriteData.story.summary}</p>
          <div className="story-source">Source: {favoriteData.story.source}</div>
        </div>
      )}
      
      {favoriteData.reasoning && (
        <div className="favorite-reasoning">
          <h4>🧠 Why This Story Made the Cut</h4>
          <p>{favoriteData.reasoning}</p>
        </div>
      )}
      
      {favoriteData.whyFascinating && (
        <div className="fascinating-factor">
          <h4>✨ The Wow Factor</h4>
          <p>{favoriteData.whyFascinating}</p>
        </div>
      )}
      
      <div className="agent-credit">
        <span className="agent-emoji">⭐</span>
        <span className="agent-text">Curated by our Favorite Selector Agent</span>
      </div>
    </div>
  );
};

export default FavoriteStory;