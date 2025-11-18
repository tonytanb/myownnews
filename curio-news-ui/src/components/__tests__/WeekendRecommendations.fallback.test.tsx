import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import WeekendRecommendations, { WeekendData } from '../WeekendRecommendations';

describe('WeekendRecommendations - Fallback Behavior', () => {
  it('renders loading state when isLoading is true', () => {
    render(<WeekendRecommendations isLoading={true} />);
    
    expect(screen.getByText('🎉 Weekend Recommendations')).toBeInTheDocument();
    expect(screen.getByText(/Our Weekend Events Agent is curating/)).toBeInTheDocument();
    expect(screen.getByText(/Analyzing trending books, movies, and local events/)).toBeInTheDocument();
  });

  it('renders loading state when weekendData is undefined', () => {
    render(<WeekendRecommendations />);
    
    expect(screen.getByText('🎉 Weekend Recommendations')).toBeInTheDocument();
    expect(screen.getByText(/Our Weekend Events Agent is curating/)).toBeInTheDocument();
  });

  it('renders fallback description when no specific content is available', () => {
    const fallbackData: WeekendData = {
      description: 'Here are some general weekend recommendations for you.'
    };

    render(<WeekendRecommendations weekendData={fallbackData} />);
    
    expect(screen.getByText('Here are some general weekend recommendations for you.')).toBeInTheDocument();
  });

  it('does not render fallback description when other content is available', () => {
    const dataWithContent: WeekendData = {
      description: 'This should not be shown',
      books: [
        {
          title: 'Test Book',
          author: 'Test Author',
          description: 'Test description',
          genre: 'Fiction'
        }
      ]
    };

    render(<WeekendRecommendations weekendData={dataWithContent} />);
    
    expect(screen.queryByText('This should not be shown')).not.toBeInTheDocument();
    expect(screen.getByText('📚 BookTok Trending')).toBeInTheDocument();
  });

  it('renders agent credit when content is available', () => {
    const dataWithContent: WeekendData = {
      books: [
        {
          title: 'Test Book',
          author: 'Test Author',
          description: 'Test description',
          genre: 'Fiction'
        }
      ]
    };

    render(<WeekendRecommendations weekendData={dataWithContent} />);
    
    expect(screen.getByText('Curated by our Weekend Events Agent')).toBeInTheDocument();
  });

  it('renders weekend badge when content is available', () => {
    const dataWithContent: WeekendData = {
      movies: [
        {
          title: 'Test Movie',
          platform: 'Netflix',
          description: 'Test description',
          genre: 'Action'
        }
      ]
    };

    render(<WeekendRecommendations weekendData={dataWithContent} />);
    
    expect(screen.getByText('AI Curated')).toBeInTheDocument();
  });

  it('handles empty weekend data gracefully', () => {
    const emptyData: WeekendData = {};

    render(<WeekendRecommendations weekendData={emptyData} />);
    
    expect(screen.getByText('🎉 Weekend Recommendations')).toBeInTheDocument();
    expect(screen.getByText('AI Curated')).toBeInTheDocument();
    expect(screen.getByText('Curated by our Weekend Events Agent')).toBeInTheDocument();
    
    // No content sections should be rendered
    expect(screen.queryByText('📚 BookTok Trending')).not.toBeInTheDocument();
    expect(screen.queryByText('🎬 Streaming Picks')).not.toBeInTheDocument();
    expect(screen.queryByText('🎪 Local Events')).not.toBeInTheDocument();
    expect(screen.queryByText('🎬 Entertainment Hub')).not.toBeInTheDocument();
  });

  it('renders mixed content correctly', () => {
    const mixedData: WeekendData = {
      books: [
        {
          title: 'Test Book',
          author: 'Test Author',
          description: 'Test description',
          genre: 'Fiction'
        }
      ],
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

    render(<WeekendRecommendations weekendData={mixedData} />);
    
    expect(screen.getByText('📚 BookTok Trending')).toBeInTheDocument();
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('Test Book')).toBeInTheDocument();
    expect(screen.getByText('Test Movie')).toBeInTheDocument();
  });

  it('handles backward compatibility with cultural_insights', () => {
    const legacyData: WeekendData = {
      cultural_insights: {
        BookTok_trends: 'Some BookTok trends',
        streaming_releases: 'New streaming releases',
        social_media_phenomena: 'Social media trends'
      }
    };

    render(<WeekendRecommendations weekendData={legacyData} />);
    
    // Component should render without crashing
    expect(screen.getByText('🎉 Weekend Recommendations')).toBeInTheDocument();
    expect(screen.getByText('AI Curated')).toBeInTheDocument();
  });

  it('prioritizes entertainment_recommendations over cultural_insights', () => {
    const dataWithBoth: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'New Movie',
            genre: 'Action',
            rating: '8.0/10',
            platform: 'Netflix',
            description: 'New entertainment system.'
          }
        ]
      },
      cultural_insights: {
        streaming_releases: 'Old cultural insights'
      }
    };

    render(<WeekendRecommendations weekendData={dataWithBoth} />);
    
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('New Movie')).toBeInTheDocument();
    // Cultural insights should not interfere with new entertainment system
  });
});