import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import WeekendRecommendations, { WeekendData } from '../WeekendRecommendations';

// Mock fetch for API calls
global.fetch = jest.fn();

describe('Entertainment Recommendations Integration Tests', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  it('handles backend entertainment data structure correctly', async () => {
    const mockBackendResponse: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'Dune: Part Two',
            genre: 'Sci-Fi Epic',
            rating: '8.8/10',
            platform: 'Max',
            description: 'Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.',
            release_year: 2024,
            runtime: '2h 46m'
          },
          {
            title: 'Oppenheimer',
            genre: 'Historical Drama',
            rating: '8.4/10',
            platform: 'Various Streaming',
            description: 'The story of J. Robert Oppenheimer and the development of the atomic bomb.',
            release_year: 2023,
            runtime: '3h 0m'
          }
        ],
        must_watch_series: [
          {
            title: 'The Bear',
            genre: 'Comedy-Drama',
            rating: '9.1/10',
            platform: 'Hulu',
            description: 'A young chef from the fine dining world returns to Chicago to run his deceased brother\'s sandwich shop.',
            seasons: 3,
            episodes_per_season: 10,
            status: 'ongoing'
          },
          {
            title: 'Wednesday',
            genre: 'Dark Comedy',
            rating: '8.1/10',
            platform: 'Netflix',
            description: 'Wednesday Addams navigates her years as a student at Nevermore Academy.',
            seasons: 2,
            episodes_per_season: 8,
            status: 'new_season'
          }
        ],
        theater_plays: [
          {
            title: 'Hamilton',
            genre: 'Musical Biography',
            venue: 'Richard Rodgers Theatre',
            city: 'New York',
            description: 'The revolutionary story of Alexander Hamilton, founding father and first Secretary of the Treasury.',
            show_times: 'Tue-Sun 8PM, Wed & Sat 2PM',
            ticket_info: 'From $79',
            rating: '9.5/10'
          }
        ]
      }
    };

    render(<WeekendRecommendations weekendData={mockBackendResponse} />);

    // Verify all entertainment categories are rendered
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('🍿 Top Movies')).toBeInTheDocument();
    expect(screen.getByText('📺 Must-Watch Series')).toBeInTheDocument();
    expect(screen.getByText('🎭 Theater & Plays')).toBeInTheDocument();

    // Verify movie content
    expect(screen.getByText('Dune: Part Two')).toBeInTheDocument();
    expect(screen.getByText('Oppenheimer')).toBeInTheDocument();
    expect(screen.getByText('Max')).toBeInTheDocument();
    expect(screen.getByText('8.8/10')).toBeInTheDocument();

    // Verify series content
    expect(screen.getByText('The Bear')).toBeInTheDocument();
    expect(screen.getByText('Wednesday')).toBeInTheDocument();
    expect(screen.getByText('3 Seasons')).toBeInTheDocument();
    expect(screen.getByText('ongoing')).toBeInTheDocument();

    // Verify theater content
    expect(screen.getByText('Hamilton')).toBeInTheDocument();
    expect(screen.getByText('📍 Richard Rodgers Theatre')).toBeInTheDocument();
    expect(screen.getByText('🕐 Tue-Sun 8PM, Wed & Sat 2PM')).toBeInTheDocument();
  });

  it('handles partial entertainment data from backend', async () => {
    const partialBackendResponse: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'Single Movie',
            genre: 'Drama',
            rating: '8.0/10',
            platform: 'Netflix',
            description: 'A single movie recommendation.'
          }
        ]
        // No series or theater plays
      }
    };

    render(<WeekendRecommendations weekendData={partialBackendResponse} />);

    // Should render entertainment hub with only movies
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('🍿 Top Movies')).toBeInTheDocument();
    expect(screen.getByText('Single Movie')).toBeInTheDocument();

    // Should not render empty categories
    expect(screen.queryByText('📺 Must-Watch Series')).not.toBeInTheDocument();
    expect(screen.queryByText('🎭 Theater & Plays')).not.toBeInTheDocument();
  });

  it('handles malformed entertainment data gracefully', async () => {
    const malformedBackendResponse: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            // Missing required fields
            title: '',
            genre: '',
            rating: '',
            platform: '',
            description: ''
          }
        ],
        must_watch_series: [
          {
            title: 'Incomplete Series',
            genre: 'Drama',
            rating: '8.0/10',
            platform: 'Netflix',
            description: 'Series with missing fields.',
            seasons: 0, // Invalid seasons
            status: 'ongoing'
          }
        ]
      }
    };

    render(<WeekendRecommendations weekendData={malformedBackendResponse} />);

    // Component should still render without crashing
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    
    // Should handle empty/invalid data gracefully
    expect(screen.getByText('Incomplete Series')).toBeInTheDocument();
    expect(screen.getByText('0 Season')).toBeInTheDocument(); // Should handle 0 seasons
  });

  it('validates entertainment data structure matches backend expectations', () => {
    // Test that our TypeScript interfaces match expected backend structure
    const validBackendData: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'Test Movie',
            genre: 'Action',
            rating: '8.0/10',
            platform: 'Netflix',
            description: 'Test description',
            release_year: 2024, // Optional field
            runtime: '2h 0m' // Optional field
          }
        ],
        must_watch_series: [
          {
            title: 'Test Series',
            genre: 'Drama',
            rating: '9.0/10',
            platform: 'Hulu',
            description: 'Test series description',
            seasons: 3,
            episodes_per_season: 10, // Optional field
            status: 'ongoing'
          }
        ],
        theater_plays: [
          {
            title: 'Test Play',
            genre: 'Musical',
            description: 'Test play description',
            venue: 'Test Theater', // Optional field
            city: 'Test City', // Optional field
            show_times: 'Daily 8PM', // Optional field
            ticket_info: 'From $50', // Optional field
            rating: '9.0/10' // Optional field
          }
        ]
      }
    };

    // This should compile without TypeScript errors and render successfully
    const { container } = render(<WeekendRecommendations weekendData={validBackendData} />);
    expect(container).toBeInTheDocument();
  });

  it('handles backward compatibility with cultural_insights', () => {
    const legacyBackendResponse: WeekendData = {
      cultural_insights: {
        BookTok_trends: 'Some trending books',
        streaming_releases: 'New releases',
        social_media_phenomena: 'Viral content'
      }
    };

    render(<WeekendRecommendations weekendData={legacyBackendResponse} />);

    // Should render without entertainment hub
    expect(screen.queryByText('🎬 Entertainment Hub')).not.toBeInTheDocument();
    
    // Should still render the main component
    expect(screen.getByText('🎉 Weekend Recommendations')).toBeInTheDocument();
  });

  it('prioritizes entertainment_recommendations over cultural_insights', () => {
    const mixedBackendResponse: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'New System Movie',
            genre: 'Action',
            rating: '8.0/10',
            platform: 'Netflix',
            description: 'From new entertainment system'
          }
        ]
      },
      cultural_insights: {
        streaming_releases: 'Old cultural insights data'
      }
    };

    render(<WeekendRecommendations weekendData={mixedBackendResponse} />);

    // Should render new entertainment system
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('New System Movie')).toBeInTheDocument();
    
    // Should not render old cultural insights
    expect(screen.queryByText('Old cultural insights data')).not.toBeInTheDocument();
  });

  it('handles empty entertainment arrays correctly', () => {
    const emptyArraysResponse: WeekendData = {
      entertainment_recommendations: {
        top_movies: [],
        must_watch_series: [],
        theater_plays: []
      }
    };

    render(<WeekendRecommendations weekendData={emptyArraysResponse} />);

    // Should not render entertainment hub when all arrays are empty
    expect(screen.queryByText('🎬 Entertainment Hub')).not.toBeInTheDocument();
  });

  it('handles missing entertainment_recommendations field', () => {
    const noEntertainmentResponse: WeekendData = {
      books: [
        {
          title: 'Test Book',
          author: 'Test Author',
          description: 'Test description',
          genre: 'Fiction'
        }
      ]
    };

    render(<WeekendRecommendations weekendData={noEntertainmentResponse} />);

    // Should render other content but not entertainment hub
    expect(screen.getByText('📚 BookTok Trending')).toBeInTheDocument();
    expect(screen.queryByText('🎬 Entertainment Hub')).not.toBeInTheDocument();
  });
});