import React, { useState } from 'react';
import './MediaGallery.css';

interface MediaImage {
  url: string;
  alt_text: string;
}

interface MediaVideo {
  url: string;
  caption: string;
}

interface StoryMedia {
  title: string;
  media_recommendations: {
    images?: MediaImage[];
    videos?: MediaVideo[];
    accessibility_features?: {
      image_alt_text?: string;
      video_captions?: string;
    };
    social_media_optimization?: {
      hashtags?: string[];
      image_dimensions?: string;
      video_aspect_ratio?: string;
    };
  };
}

interface MediaData {
  stories?: StoryMedia[];
  description?: string;
}

interface MediaGalleryProps {
  mediaData?: MediaData;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  retryAttempt?: number;
  maxRetries?: number;
}

const MediaGallery: React.FC<MediaGalleryProps> = ({ 
  mediaData, 
  isLoading, 
  error, 
  onRetry, 
  retryAttempt = 0, 
  maxRetries = 3 
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  // Show error state
  if (error) {
    const canRetry = onRetry && retryAttempt < maxRetries;
    const isMaxRetries = retryAttempt >= maxRetries;
    
    return (
      <div className="media-section">
        <div className="media-header">
          <h3>🎨 Visual Enhancements</h3>
          <span className="error-badge">Failed</span>
        </div>
        <div className="media-error">
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
                <p>The Media Enhancer Agent may be experiencing technical difficulties.</p>
                <p>💡 <strong>Fallback:</strong> The news stories above still have great content to read!</p>
              </div>
            ) : (
              <div className="error-help">
                <p>🤖 Our Media Enhancer Agent encountered an issue while selecting visuals.</p>
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
                🔄 Retry Visual Enhancements ({maxRetries - retryAttempt} attempts left)
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
  if (isLoading || !mediaData) {
    return (
      <div className="media-section">
        <h3>🎨 Visual Enhancements</h3>
        <div className="media-placeholder">
          <div className="loading-spinner">⏳</div>
          <p>🤖 Our Media Enhancer Agent is selecting compelling visuals and optimizing content...</p>
          <div className="loading-progress">
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
            <p className="progress-text">Curating images, optimizing accessibility, and preparing social media assets...</p>
          </div>
        </div>
      </div>
    );
  }

  const handleImageClick = (imageUrl: string) => {
    setSelectedImage(imageUrl);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  return (
    <div className="media-section">
      <div className="media-header">
        <h3>🎨 Visual Enhancements</h3>
        <span className="media-badge">AI Enhanced</span>
      </div>

      {mediaData.stories && mediaData.stories.length > 0 ? (
        <div className="media-summary">
          <div className="enhancement-stats">
            <div className="stat-item">
              <span className="stat-number">{mediaData.stories.length}</span>
              <span className="stat-label">Stories Enhanced</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">
                {mediaData.stories.reduce((total, story) => 
                  total + (story.media_recommendations.images?.length || 0), 0
                )}
              </span>
              <span className="stat-label">Images Curated</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">
                {mediaData.stories.reduce((total, story) => 
                  total + (story.media_recommendations.videos?.length || 0), 0
                )}
              </span>
              <span className="stat-label">Videos Selected</span>
            </div>
          </div>
          
          <div className="enhancement-features">
            <h4>🎨 AI Enhancement Features</h4>
            <div className="features-grid">
              <div className="feature-item">
                <span className="feature-icon">🖼️</span>
                <div className="feature-content">
                  <h5>Visual Content</h5>
                  <p>AI-selected images and videos for each story with descriptive alt-text</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">♿</span>
                <div className="feature-content">
                  <h5>Accessibility</h5>
                  <p>Screen reader support, captions, and high contrast optimization</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📱</span>
                <div className="feature-content">
                  <h5>Social Ready</h5>
                  <p>Optimized hashtags, dimensions, and formats for social sharing</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🎯</span>
                <div className="feature-content">
                  <h5>Smart Curation</h5>
                  <p>Content matched to story themes and audience preferences</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="view-details">
            <p>💡 <strong>Images and hashtags are now integrated directly into each news story above!</strong></p>
            <p>The Media Enhancer Agent has analyzed each story and provided visual content, accessibility features, and social media optimization.</p>
          </div>
        </div>
      ) : (
        <div className="media-description">
          <p>{mediaData.description || 'Media enhancements are being processed...'}</p>
        </div>
      )}

      <div className="agent-credit">
        <span className="agent-emoji">🎨</span>
        <span className="agent-text">Enhanced by our Media Enhancer Agent</span>
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div className="image-modal" onClick={closeModal}>
          <div className="modal-content">
            <button className="close-modal" onClick={closeModal}>✕</button>
            <div className="modal-image-placeholder">
              <span className="modal-image-icon">🖼️</span>
              <p>Image Preview</p>
              <p className="modal-image-url">{selectedImage}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaGallery;