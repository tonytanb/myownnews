import React from 'react';
import { TheaterPlay } from './WeekendRecommendations';

interface PlayCardProps {
  play: TheaterPlay;
}

const PlayCard: React.FC<PlayCardProps> = ({ play }) => {
  // Generate Google search URL for theater plays
  const getTheaterSearchUrl = (title: string, city?: string) => {
    const searchQuery = city ? `${title} theater ${city} tickets` : `${title} theater tickets`;
    return `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;
  };

  const searchUrl = getTheaterSearchUrl(play.title, play.city);

  return (
    <a 
      href={searchUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="entertainment-card play-card"
      style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
    >
      {play.image && (
        <div className="card-image" style={{ 
          backgroundImage: `url(${play.image})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          height: '180px',
          borderRadius: '8px 8px 0 0',
          marginBottom: '12px'
        }} />
      )}
      <div className="card-header">
        {play.rating && <div className="rating-badge">{play.rating}</div>}
      </div>
      <h6 className="entertainment-title">{play.title}</h6>
      <div className="entertainment-meta">
        <span className="genre">{play.genre}</span>
        {play.venue && <span className="venue">📍 {play.venue}</span>}
        {play.city && <span className="city">{play.city}</span>}
      </div>
      <p className="entertainment-description">{play.description}</p>
      {play.show_times && (
        <div className="show-info">
          <span className="show-times">🕐 {play.show_times}</span>
        </div>
      )}
      {play.ticket_info && (
        <div className="ticket-info">
          <span className="tickets">🎫 {play.ticket_info}</span>
        </div>
      )}
      <div className="external-link-indicator">
        <span>Find Tickets →</span>
      </div>
    </a>
  );
};

export default PlayCard;