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

interface NewsItemsProps {
  items: NewsItem[];
  mediaEnhancements?: any;
  favoriteData?: any;
}

const NewsItems: React.FC<NewsItemsProps> = ({ items, favoriteData }) => {
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());

  const toggleExpand = (index: number) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedItems(newExpanded);
  };

  const truncateText = (text: string, lines: number = 4): string => {
    // Don't truncate - show the full summary from backend
    // Backend already ensures summaries are clean and complete
    return text;
  };

  if (!items || items.length === 0) {
    return (
      <div className="news-items-section">
        <h3>Today's Curated Stories</h3>
        <div className="news-loading">Loading news...</div>
      </div>
    );
  }

  return (
    <div className="news-items-section">
      <h3>Today's Curated Stories ({items.length})</h3>
      <div className="news-items-list">
        {items.map((item, index) => {
          const isExpanded = expandedItems.has(index);
          const displaySummary = isExpanded ? item.summary : truncateText(item.summary, 4);
          const isFavorite = index === 0 && favoriteData;

          return (
            <div 
              key={index} 
              className={`news-card ${isExpanded ? 'expanded' : ''} ${isFavorite ? 'favorite-card' : ''}`}
              onClick={() => toggleExpand(index)}
              style={{ cursor: 'pointer' }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  toggleExpand(index);
                }
              }}
              aria-expanded={isExpanded}
            >
              {/* Thumbnail - only show when collapsed */}
              {!isExpanded && (
                <div className="news-thumbnail">
                  {item.image ? (
                    <img src={item.image} alt={item.title} />
                  ) : (
                    <div className="news-thumbnail-placeholder">
                      {item.category === 'Technology' && '💻'}
                      {item.category === 'Science' && '🔬'}
                      {item.category === 'Politics' && '🏛️'}
                      {item.category === 'Business' && '💼'}
                      {item.category === 'Health' && '🏥'}
                      {item.category === 'Environment' && '🌍'}
                      {item.category === 'Sports' && '⚽'}
                      {item.category === 'Entertainment' && '🎬'}
                      {!['Technology', 'Science', 'Politics', 'Business', 'Health', 'Environment', 'Sports', 'Entertainment'].includes(item.category) && '📰'}
                    </div>
                  )}
                </div>
              )}

              <div className="news-card-content">
                <div className="news-card-header">
                  <div className="news-card-meta">
                    <span className="news-category">{item.category}</span>
                    {item.source && (
                      <span className="news-source">{item.source}</span>
                    )}
                  </div>
                  <div className="expand-indicator">
                    {isExpanded ? '−' : '+'}
                  </div>
                </div>

                <h4 className="news-title">{item.title}</h4>
                
                <p className="news-summary">{displaySummary}</p>

                {isExpanded && item.full_text && (
                  <div className="news-full-text">
                    <p>{item.full_text}</p>
                  </div>
                )}

                {isExpanded && item.image && (
                  <div className="news-image-expanded">
                    <img src={item.image} alt={item.title} />
                  </div>
                )}

                {isExpanded && item.relevance_score && (
                  <div className="news-metadata">
                    <span className="relevance-badge">
                      Relevance: {Math.round(item.relevance_score * 100)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default NewsItems;
