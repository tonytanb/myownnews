import React from 'react';
import { TopMovie } from './WeekendRecommendations';

interface MovieCardProps {
  movie: TopMovie;
}

const MovieCard: React.FC<MovieCardProps> = ({ movie }) => {
  // Generate IMDB search URL
  const getIMDBSearchUrl = (title: string, year?: number) => {
    const searchQuery = year ? `${title} ${year}` : title;
    return `https://www.imdb.com/find?q=${encodeURIComponent(searchQuery)}&s=tt&ttype=ft`;
  };

  const imdbUrl = getIMDBSearchUrl(movie.title, movie.release_year);

  return (
    <a 
      href={imdbUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="entertainment-card movie-card"
      style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
    >
      {movie.image && (
        <div className="card-image" style={{ 
          backgroundImage: `url(${movie.image})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          height: '180px',
          borderRadius: '8px 8px 0 0',
          marginBottom: '12px'
        }} />
      )}
      <div className="card-header">
        <div className="platform-badge">{movie.platform}</div>
        <div className="rating-badge">{movie.rating}</div>
      </div>
      <h6 className="entertainment-title">{movie.title}</h6>
      <div className="entertainment-meta">
        <span className="genre">{movie.genre}</span>
        {movie.runtime && <span className="runtime">{movie.runtime}</span>}
        {movie.release_year && <span className="year">{movie.release_year}</span>}
      </div>
      <p className="entertainment-description">{movie.description}</p>
      <div className="external-link-indicator">
        <span>View on IMDB →</span>
      </div>
    </a>
  );
};

export default MovieCard;