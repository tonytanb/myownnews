import React, { useState } from 'react';
import './NewsItems.css';

interface NewsItem {
  title: string;
  category: string;
  summary: string;
  full_text?: string;
  image?: string;
  relevance_score?: number;
  source?: string;
}

interface MediaEnhancement {
  title: string;
  media_recommendations: {
    images?: Array<{
      url: string;
      alt_text: string;
    }>;
    videos?: Array<{
      url: string;
      caption: string;
    }>;
    social_media_optimization?: {
      hashtags?: string[];
    };
  };
}

interface NewsItemsProps {
  items: NewsItem[];
  mediaEnhancements?: {
    stories?: MediaEnhancement[];
  };
}

interface NewsImageProps {
  imageData?: {
    url: string;
    alt_text: string;
  };
  category?: string;
  title: string;
}

const NewsImage: React.FC<NewsImageProps> = ({ imageData, category, title }) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  // Generate a fallback image URL based on the story content
  const getFallbackImageUrl = (title: string, category: string) => {
    // Use Unsplash for high-quality stock photos based on keywords
    const keywords = extractKeywords(title, category);
    return `https://source.unsplash.com/800x400/?${keywords}`;
  };

  // Extract relevant keywords from title and category for image search
  const extractKeywords = (title: string, category: string) => {
    const titleWords = title.toLowerCase().split(' ');
    const techKeywords = ['technology', 'ai', 'computer', 'software', 'tech'];
    const businessKeywords = ['business', 'finance', 'money', 'corporate'];
    const scienceKeywords = ['science', 'research', 'laboratory', 'discovery'];
    const politicsKeywords = ['politics', 'government', 'law', 'policy'];
    const cultureKeywords = ['culture', 'art', 'entertainment', 'music'];

    // Look for specific keywords in the title
    if (titleWords.some(word => ['ai', 'artificial', 'intelligence', 'openai', 'google'].includes(word))) {
      return 'artificial-intelligence,technology';
    }
    if (titleWords.some(word => ['startup', 'funding', 'vc', 'venture'].includes(word))) {
      return 'startup,business,office';
    }
    if (titleWords.some(word => ['hollywood', 'movie', 'film', 'entertainment'].includes(word))) {
      return 'hollywood,cinema,entertainment';
    }
    if (titleWords.some(word => ['apple', 'iphone', 'ios'].includes(word))) {
      return 'apple,technology,smartphone';
    }

    // Fallback to category-based keywords
    switch (category?.toUpperCase()) {
      case 'TECHNOLOGY':
        return techKeywords.join(',');
      case 'BUSINESS':
        return businessKeywords.join(',');
      case 'SCIENCE':
        return scienceKeywords.join(',');
      case 'POLITICS':
        return politicsKeywords.join(',');
      case 'CULTURE':
        return cultureKeywords.join(',');
      default:
        return 'news,abstract,modern';
    }
  };

  const getCategoryIcon = (category?: string) => {
    switch (category?.toUpperCase()) {
      case 'TECHNOLOGY': return '💻';
      case 'POLITICS': return '🏛️';
      case 'SCIENCE': return '🔬';
      case 'CULTURE': return '🎭';
      case 'BUSINESS': return '💼';
      default: return '📰';
    }
  };

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };

  // Determine which image to show
  const shouldShowRealImage = imageData && imageData.url && !imageData.url.includes('example.com') && !imageError;
  const imageUrl = shouldShowRealImage ? imageData.url : getFallbackImageUrl(title, category || '');

  return (
    <div className="news-image-container">
      {shouldShowRealImage || !imageError ? (
        <div className="news-image-wrapper">
          {imageLoading && (
            <div className="news-image-placeholder loading">
              <span className="loading-spinner">⏳</span>
              <p>Loading image...</p>
            </div>
          )}
          <img
            src={imageUrl}
            alt={imageData?.alt_text || `${category} news image`}
            className={`news-image ${imageLoading ? 'hidden' : ''}`}
            onLoad={handleImageLoad}
            onError={handleImageError}
          />
          {imageData?.alt_text && !imageLoading && (
            <div className="image-caption">{imageData.alt_text}</div>
          )}
        </div>
      ) : (
        <div className="news-image-placeholder default">
          <span className="category-icon">{getCategoryIcon(category)}</span>
          <p className="category-label">{category || 'NEWS'}</p>
        </div>
      )}
    </div>
  );
};

const NewsItems: React.FC<NewsItemsProps> = ({ items, mediaEnhancements }) => {
  
  // Helper function to find media for a news item
  const findMediaForStory = (title: string) => {
    if (!mediaEnhancements?.stories) return null;
    
    // Try to find exact match first
    let match = mediaEnhancements.stories.find(story => 
      story.title.toLowerCase().includes(title.toLowerCase().substring(0, 30)) ||
      title.toLowerCase().includes(story.title.toLowerCase().substring(0, 30))
    );
    
    // If no match found, try with shorter substring
    if (!match) {
      match = mediaEnhancements.stories.find(story => 
        story.title.toLowerCase().includes(title.toLowerCase().substring(0, 15)) ||
        title.toLowerCase().includes(story.title.toLowerCase().substring(0, 15))
      );
    }
    
    return match;
  };
  if (!items || items.length === 0) {
    return (
      <div className="news-items-section">
        <h2>📰 Source Articles</h2>
        <div className="news-loading">
          <p>Loading news items...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="news-items-section">
      <h2>📰 Source Articles ({items.length})</h2>
      <div className="news-items-grid">
        {items.map((item, index) => {
          const mediaData = findMediaForStory(item.title);
          const primaryImage = mediaData?.media_recommendations?.images?.[0];
          const hashtags = mediaData?.media_recommendations?.social_media_optimization?.hashtags;
          
          return (
            <div key={index} className="news-item">
              {/* Image Section */}
              <NewsImage 
                imageData={primaryImage}
                category={item.category}
                title={item.title}
              />
              
              {/* Content Section */}
              <div className="news-content">
                <div className="news-category">{item.category || 'NEWS'}</div>
                <h3 className="news-title">{item.title}</h3>
                <p className="news-summary">{item.summary}</p>
                
                {/* Social Media Tags */}
                {hashtags && hashtags.length > 0 && (
                  <div className="news-hashtags">
                    {hashtags.slice(0, 3).map((tag, tagIndex) => (
                      <span key={tagIndex} className="hashtag">{tag}</span>
                    ))}
                  </div>
                )}
                
                {/* Metadata */}
                <div className="news-metadata">
                  {item.relevance_score && (
                    <div className="relevance-score">
                      Relevance: {Math.round(item.relevance_score * 100)}%
                    </div>
                  )}
                  {item.source && (
                    <div className="news-source">
                      Source: {item.source}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NewsItems;