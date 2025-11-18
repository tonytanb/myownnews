import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import SeriesCard from '../SeriesCard';
import { TVSeries } from '../WeekendRecommendations';

describe('SeriesCard', () => {
  const mockSeries: TVSeries = {
    title: 'The Bear',
    genre: 'Comedy-Drama',
    rating: '9.1/10',
    platform: 'Hulu',
    description: 'A young chef from the fine dining world returns to Chicago to run his deceased brother\'s sandwich shop.',
    seasons: 3,
    episodes_per_season: 10,
    status: 'ongoing'
  };

  it('renders series card with all required information', () => {
    render(<SeriesCard series={mockSeries} />);
    
    expect(screen.getByText('The Bear')).toBeInTheDocument();
    expect(screen.getByText('Comedy-Drama')).toBeInTheDocument();
    expect(screen.getByText('9.1/10')).toBeInTheDocument();
    expect(screen.getByText('Hulu')).toBeInTheDocument();
    expect(screen.getByText(/A young chef from the fine dining world/)).toBeInTheDocument();
    expect(screen.getByText('3 Seasons')).toBeInTheDocument();
    expect(screen.getByText('10 eps/season')).toBeInTheDocument();
    expect(screen.getByText('ongoing')).toBeInTheDocument();
  });

  it('renders singular season correctly', () => {
    const singleSeasonSeries: TVSeries = {
      title: 'Limited Series',
      genre: 'Drama',
      rating: '8.0/10',
      platform: 'Netflix',
      description: 'A limited series.',
      seasons: 1,
      status: 'completed'
    };

    render(<SeriesCard series={singleSeasonSeries} />);
    
    expect(screen.getByText('1 Season')).toBeInTheDocument();
  });

  it('renders series card without optional episodes_per_season', () => {
    const seriesWithoutEpisodes: TVSeries = {
      title: 'Mystery Series',
      genre: 'Mystery',
      rating: '7.8/10',
      platform: 'Prime Video',
      description: 'A mysterious series.',
      seasons: 2,
      status: 'new_season'
    };

    render(<SeriesCard series={seriesWithoutEpisodes} />);
    
    expect(screen.getByText('Mystery Series')).toBeInTheDocument();
    expect(screen.getByText('2 Seasons')).toBeInTheDocument();
    expect(screen.queryByText(/eps\/season/)).not.toBeInTheDocument();
    expect(screen.getByText('new season')).toBeInTheDocument();
  });

  it('applies correct CSS classes for different statuses', () => {
    const { container } = render(<SeriesCard series={mockSeries} />);
    
    expect(container.querySelector('.entertainment-card')).toBeInTheDocument();
    expect(container.querySelector('.series-card')).toBeInTheDocument();
    expect(container.querySelector('.status-badge')).toBeInTheDocument();
    expect(container.querySelector('.status-ongoing')).toBeInTheDocument();
  });

  it('handles status replacement correctly', () => {
    const newSeasonSeries: TVSeries = {
      title: 'New Season Show',
      genre: 'Action',
      rating: '8.5/10',
      platform: 'Disney+',
      description: 'Action packed series.',
      seasons: 4,
      status: 'new_season'
    };

    render(<SeriesCard series={newSeasonSeries} />);
    
    expect(screen.getByText('new season')).toBeInTheDocument();
  });

  it('renders all status types correctly', () => {
    const statuses: Array<TVSeries['status']> = ['ongoing', 'completed', 'new_season'];
    
    statuses.forEach(status => {
      const series: TVSeries = {
        title: `Test Series ${status}`,
        genre: 'Test',
        rating: '8.0/10',
        platform: 'Test Platform',
        description: 'Test description',
        seasons: 1,
        status
      };

      const { container } = render(<SeriesCard series={series} />);
      expect(container.querySelector(`.status-${status}`)).toBeInTheDocument();
    });
  });
});