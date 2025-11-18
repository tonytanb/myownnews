import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MovieCard from '../MovieCard';
import { TopMovie } from '../WeekendRecommendations';

describe('MovieCard', () => {
  const mockMovie: TopMovie = {
    title: 'Dune: Part Two',
    genre: 'Sci-Fi Epic',
    rating: '8.8/10',
    platform: 'Max',
    description: 'Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.',
    release_year: 2024,
    runtime: '2h 46m'
  };

  it('renders movie card with all required information', () => {
    render(<MovieCard movie={mockMovie} />);
    
    expect(screen.getByText('Dune: Part Two')).toBeInTheDocument();
    expect(screen.getByText('Sci-Fi Epic')).toBeInTheDocument();
    expect(screen.getByText('8.8/10')).toBeInTheDocument();
    expect(screen.getByText('Max')).toBeInTheDocument();
    expect(screen.getByText(/Paul Atreides unites with Chani/)).toBeInTheDocument();
    expect(screen.getByText('2024')).toBeInTheDocument();
    expect(screen.getByText('2h 46m')).toBeInTheDocument();
  });

  it('renders movie card without optional fields', () => {
    const minimalMovie: TopMovie = {
      title: 'Simple Movie',
      genre: 'Drama',
      rating: '7.5/10',
      platform: 'Netflix',
      description: 'A simple movie description.'
    };

    render(<MovieCard movie={minimalMovie} />);
    
    expect(screen.getByText('Simple Movie')).toBeInTheDocument();
    expect(screen.getByText('Drama')).toBeInTheDocument();
    expect(screen.getByText('7.5/10')).toBeInTheDocument();
    expect(screen.getByText('Netflix')).toBeInTheDocument();
    expect(screen.getByText('A simple movie description.')).toBeInTheDocument();
    
    // Optional fields should not be present
    expect(screen.queryByText('2024')).not.toBeInTheDocument();
    expect(screen.queryByText('2h 46m')).not.toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    const { container } = render(<MovieCard movie={mockMovie} />);
    
    expect(container.querySelector('.entertainment-card')).toBeInTheDocument();
    expect(container.querySelector('.movie-card')).toBeInTheDocument();
    expect(container.querySelector('.card-header')).toBeInTheDocument();
    expect(container.querySelector('.platform-badge')).toBeInTheDocument();
    expect(container.querySelector('.rating-badge')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-title')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-meta')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-description')).toBeInTheDocument();
  });

  it('handles empty strings gracefully', () => {
    const movieWithEmptyFields: TopMovie = {
      title: '',
      genre: '',
      rating: '',
      platform: '',
      description: '',
      release_year: 0,
      runtime: ''
    };

    render(<MovieCard movie={movieWithEmptyFields} />);
    
    // Component should still render without crashing
    expect(screen.getByRole('heading', { level: 6 })).toBeInTheDocument();
  });
});