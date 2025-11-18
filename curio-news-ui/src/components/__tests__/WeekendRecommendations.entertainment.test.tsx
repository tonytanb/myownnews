import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import WeekendRecommendations, { WeekendData } from '../WeekendRecommendations';

describe('WeekendRecommendations - Entertainment Hub', () => {
  const mockEntertainmentData: WeekendData = {
    entertainment_recommendations: {
      top_movies: [
        {
          title: 'Dune: Part Two',
          genre: 'Sci-Fi Epic',
          rating: '8.8/10',
          platform: 'Max',
          description: 'Paul Atreides unites with Chani and the Fremen.',
          release_year: 2024,
          runtime: '2h 46m'
        }
      ],
      must_watch_series: [
        {
          title: 'The Bear',
          genre: 'Comedy-Drama',
          rating: '9.1/10',
          platform: 'Hulu',
          description: 'A young chef returns to Chicago.',
          seasons: 3,
          status: 'ongoing'
        }
      ],
      theater_plays: [
        {
          title: 'Hamilton',
          genre: 'Musical',
          venue: 'Richard Rodgers Theatre',
          city: 'New York',
          description: 'The story of Alexander Hamilton.',
          show_times: 'Tue-Sun 8PM',
          ticket_info: 'From $79',
          rating: '9.5/10'
        }
      ]
    }
  };

  it('renders entertainment hub with all categories', () => {
    render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('🍿 Top Movies')).toBeInTheDocument();
    expect(screen.getByText('📺 Must-Watch Series')).toBeInTheDocument();
    expect(screen.getByText('🎭 Theater & Plays')).toBeInTheDocument();
    
    // Check that content from each category is rendered
    expect(screen.getByText('Dune: Part Two')).toBeInTheDocument();
    expect(screen.getByText('The Bear')).toBeInTheDocument();
    expect(screen.getByText('Hamilton')).toBeInTheDocument();
  });

  it('renders entertainment hub with only movies', () => {
    const moviesOnlyData: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'Test Movie',
            genre: 'Action',
            rating: '8.0/10',
            platform: 'Netflix',
            description: 'Test movie description.'
          }
        ]
      }
    };

    render(<WeekendRecommendations weekendData={moviesOnlyData} />);
    
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('🍿 Top Movies')).toBeInTheDocument();
    expect(screen.getByText('Test Movie')).toBeInTheDocument();
    
    // Other categories should not be present
    expect(screen.queryByText('📺 Must-Watch Series')).not.toBeInTheDocument();
    expect(screen.queryByText('🎭 Theater & Plays')).not.toBeInTheDocument();
  });

  it('renders entertainment hub with only series', () => {
    const seriesOnlyData: WeekendData = {
      entertainment_recommendations: {
        must_watch_series: [
          {
            title: 'Test Series',
            genre: 'Drama',
            rating: '7.5/10',
            platform: 'Prime Video',
            description: 'Test series description.',
            seasons: 2,
            status: 'completed'
          }
        ]
      }
    };

    render(<WeekendRecommendations weekendData={seriesOnlyData} />);
    
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('📺 Must-Watch Series')).toBeInTheDocument();
    expect(screen.getByText('Test Series')).toBeInTheDocument();
    
    // Other categories should not be present
    expect(screen.queryByText('🍿 Top Movies')).not.toBeInTheDocument();
    expect(screen.queryByText('🎭 Theater & Plays')).not.toBeInTheDocument();
  });

  it('renders entertainment hub with only plays', () => {
    const playsOnlyData: WeekendData = {
      entertainment_recommendations: {
        theater_plays: [
          {
            title: 'Test Play',
            genre: 'Comedy',
            description: 'Test play description.'
          }
        ]
      }
    };

    render(<WeekendRecommendations weekendData={playsOnlyData} />);
    
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('🎭 Theater & Plays')).toBeInTheDocument();
    expect(screen.getByText('Test Play')).toBeInTheDocument();
    
    // Other categories should not be present
    expect(screen.queryByText('🍿 Top Movies')).not.toBeInTheDocument();
    expect(screen.queryByText('📺 Must-Watch Series')).not.toBeInTheDocument();
  });

  it('does not render entertainment hub when no entertainment data', () => {
    const noEntertainmentData: WeekendData = {
      books: [
        {
          title: 'Test Book',
          author: 'Test Author',
          description: 'Test description',
          genre: 'Fiction'
        }
      ]
    };

    render(<WeekendRecommendations weekendData={noEntertainmentData} />);
    
    expect(screen.queryByText('🎬 Entertainment Hub')).not.toBeInTheDocument();
    expect(screen.queryByText('🍿 Top Movies')).not.toBeInTheDocument();
    expect(screen.queryByText('📺 Must-Watch Series')).not.toBeInTheDocument();
    expect(screen.queryByText('🎭 Theater & Plays')).not.toBeInTheDocument();
  });

  it('does not render entertainment hub when entertainment_recommendations is empty', () => {
    const emptyEntertainmentData: WeekendData = {
      entertainment_recommendations: {}
    };

    render(<WeekendRecommendations weekendData={emptyEntertainmentData} />);
    
    expect(screen.queryByText('🎬 Entertainment Hub')).not.toBeInTheDocument();
  });

  it('does not render categories with empty arrays', () => {
    const emptyArraysData: WeekendData = {
      entertainment_recommendations: {
        top_movies: [],
        must_watch_series: [],
        theater_plays: []
      }
    };

    render(<WeekendRecommendations weekendData={emptyArraysData} />);
    
    expect(screen.queryByText('🎬 Entertainment Hub')).not.toBeInTheDocument();
  });

  it('renders multiple items in each category', () => {
    const multipleItemsData: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'Movie 1',
            genre: 'Action',
            rating: '8.0/10',
            platform: 'Netflix',
            description: 'First movie.'
          },
          {
            title: 'Movie 2',
            genre: 'Comedy',
            rating: '7.5/10',
            platform: 'Hulu',
            description: 'Second movie.'
          }
        ],
        must_watch_series: [
          {
            title: 'Series 1',
            genre: 'Drama',
            rating: '9.0/10',
            platform: 'HBO',
            description: 'First series.',
            seasons: 1,
            status: 'completed'
          },
          {
            title: 'Series 2',
            genre: 'Thriller',
            rating: '8.5/10',
            platform: 'Prime Video',
            description: 'Second series.',
            seasons: 3,
            status: 'ongoing'
          }
        ]
      }
    };

    render(<WeekendRecommendations weekendData={multipleItemsData} />);
    
    expect(screen.getByText('Movie 1')).toBeInTheDocument();
    expect(screen.getByText('Movie 2')).toBeInTheDocument();
    expect(screen.getByText('Series 1')).toBeInTheDocument();
    expect(screen.getByText('Series 2')).toBeInTheDocument();
  });

  it('applies correct CSS classes for entertainment hub', () => {
    const { container } = render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    expect(container.querySelector('.entertainment-hub')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-categories')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-category')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-grid')).toBeInTheDocument();
  });
});