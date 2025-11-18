import React from 'react';
import { TVSeries } from './WeekendRecommendations';

interface SeriesCardProps {
  series: TVSeries;
}

const SeriesCard: React.FC<SeriesCardProps> = ({ series }) => {
  // Generate IMDB search URL for TV series
  const getIMDBSearchUrl = (title: string) => {
    return `https://www.imdb.com/find?q=${encodeURIComponent(title)}&s=tt&ttype=tv`;
  };

  const imdbUrl = getIMDBSearchUrl(series.title);

  return (
    <a 
      href={imdbUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="entertainment-card series-card"
      style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
    >
      {series.image && (
        <div className="card-image" style={{ 
          backgroundImage: `url(${series.image})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          height: '180px',
          borderRadius: '8px 8px 0 0',
          marginBottom: '12px'
        }} />
      )}
      <div className="card-header">
        <div className="platform-badge">{series.platform}</div>
        <div className="rating-badge">{series.rating}</div>
      </div>
      <h6 className="entertainment-title">{series.title}</h6>
      <div className="entertainment-meta">
        <span className="genre">{series.genre}</span>
        <span className="seasons">{series.seasons} Season{series.seasons > 1 ? 's' : ''}</span>
        <span className={`status-badge status-${series.status}`}>
          {series.status.replace('_', ' ')}
        </span>
        {series.episodes_per_season && (
          <span className="episodes">{series.episodes_per_season} eps/season</span>
        )}
      </div>
      <p className="entertainment-description">{series.description}</p>
      <div className="external-link-indicator">
        <span>View on IMDB →</span>
      </div>
    </a>
  );
};

export default SeriesCard;