import React from 'react';
import './NewsItems.css';

interface NewsItem {
  title: string;
  category: string;
  summary: string;
  full_text: string;
}

interface NewsItemsProps {
  items: NewsItem[];
}

const NewsItems: React.FC<NewsItemsProps> = ({ items }) => {
  return (
    <div className="news-items-section">
      <h2>📰 Source Articles</h2>
      <div className="news-items-grid">
        {items.map((item, index) => (
          <div key={index} className="news-item">
            <div className="news-category">{item.category}</div>
            <h3 className="news-title">{item.title}</h3>
            <p className="news-summary">{item.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NewsItems;