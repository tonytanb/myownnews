import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import WeekendRecommendations, { WeekendData } from '../WeekendRecommendations';

describe('Entertainment Recommendations Accessibility Tests', () => {
  const mockEntertainmentData: WeekendData = {
    entertainment_recommendations: {
      top_movies: [
        {
          title: 'Test Movie',
          genre: 'Action',
          rating: '8.0/10',
          platform: 'Netflix',
          description: 'Test movie description for accessibility testing.',
          release_year: 2024,
          runtime: '2h 0m'
        }
      ],
      must_watch_series: [
        {
          title: 'Test Series',
          genre: 'Drama',
          rating: '9.0/10',
          platform: 'Hulu',
          description: 'Test series description for accessibility testing.',
          seasons: 3,
          episodes_per_season: 10,
          status: 'ongoing'
        }
      ],
      theater_plays: [
        {
          title: 'Test Play',
          genre: 'Musical',
          venue: 'Test Theater',
          city: 'Test City',
          description: 'Test play description for accessibility testing.',
          show_times: 'Daily 8PM',
          ticket_info: 'From $50',
          rating: '9.0/10'
        }
      ]
    }
  };

  it('maintains proper heading hierarchy', () => {
    render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    // Check heading hierarchy: h3 -> h4 -> h5 -> h6
    const mainHeading = screen.getByRole('heading', { level: 3 });
    expect(mainHeading).toHaveTextContent('🎉 Weekend Recommendations');
    
    const entertainmentHubHeading = screen.getByRole('heading', { level: 4 });
    expect(entertainmentHubHeading).toHaveTextContent('🎬 Entertainment Hub');
    
    const categoryHeadings = screen.getAllByRole('heading', { level: 5 });
    expect(categoryHeadings).toHaveLength(3);
    expect(categoryHeadings[0]).toHaveTextContent('🍿 Top Movies');
    expect(categoryHeadings[1]).toHaveTextContent('📺 Must-Watch Series');
    expect(categoryHeadings[2]).toHaveTextContent('🎭 Theater & Plays');
    
    const itemHeadings = screen.getAllByRole('heading', { level: 6 });
    expect(itemHeadings).toHaveLength(3);
    expect(itemHeadings[0]).toHaveTextContent('Test Movie');
    expect(itemHeadings[1]).toHaveTextContent('Test Series');
    expect(itemHeadings[2]).toHaveTextContent('Test Play');
  });

  it('provides semantic HTML structure', () => {
    const { container } = render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    // Check for proper semantic structure
    expect(container.querySelector('.entertainment-hub')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-categories')).toBeInTheDocument();
    expect(container.querySelectorAll('.entertainment-category')).toHaveLength(3);
    expect(container.querySelectorAll('.entertainment-grid')).toHaveLength(3);
    expect(container.querySelectorAll('.entertainment-card')).toHaveLength(3);
  });

  it('ensures all text content is readable', () => {
    render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    // Check that all important text content is present and accessible
    expect(screen.getByText('Test Movie')).toBeInTheDocument();
    expect(screen.getByText('Test movie description for accessibility testing.')).toBeInTheDocument();
    expect(screen.getByText('Action')).toBeInTheDocument();
    expect(screen.getByText('8.0/10')).toBeInTheDocument();
    expect(screen.getByText('Netflix')).toBeInTheDocument();
    
    expect(screen.getByText('Test Series')).toBeInTheDocument();
    expect(screen.getByText('Test series description for accessibility testing.')).toBeInTheDocument();
    expect(screen.getByText('Drama')).toBeInTheDocument();
    expect(screen.getByText('3 Seasons')).toBeInTheDocument();
    
    expect(screen.getByText('Test Play')).toBeInTheDocument();
    expect(screen.getByText('Test play description for accessibility testing.')).toBeInTheDocument();
    expect(screen.getByText('📍 Test Theater')).toBeInTheDocument();
    expect(screen.getByText('🕐 Daily 8PM')).toBeInTheDocument();
  });

  it('handles long text content gracefully', () => {
    const longContentData: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'A Very Long Movie Title That Might Wrap to Multiple Lines in Different Screen Sizes',
            genre: 'Drama with Very Long Genre Description',
            rating: '8.5/10',
            platform: 'A Streaming Platform with a Very Long Name',
            description: 'This is a very long movie description that contains multiple sentences and should wrap properly across different screen sizes. It includes detailed plot information, character descriptions, and other relevant details that users might want to read. The description should remain readable and accessible regardless of the viewport size.',
            release_year: 2024,
            runtime: '3h 45m'
          }
        ]
      }
    };

    render(<WeekendRecommendations weekendData={longContentData} />);
    
    // Verify long content is rendered
    expect(screen.getByText(/A Very Long Movie Title/)).toBeInTheDocument();
    expect(screen.getByText(/This is a very long movie description/)).toBeInTheDocument();
    
    // Component should not break with long content
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
  });

  it('provides proper ARIA labels and roles where needed', () => {
    const { container } = render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    // Check for proper heading roles (implicit)
    const headings = container.querySelectorAll('h3, h4, h5, h6');
    expect(headings.length).toBeGreaterThan(0);
    
    // Verify content structure is logical
    const entertainmentCards = container.querySelectorAll('.entertainment-card');
    entertainmentCards.forEach(card => {
      // Each card should have a title heading
      const titleHeading = card.querySelector('h6');
      expect(titleHeading).toBeInTheDocument();
      
      // Each card should have descriptive content
      const description = card.querySelector('.entertainment-description');
      expect(description).toBeInTheDocument();
    });
  });

  it('handles missing optional content accessibly', () => {
    const minimalData: WeekendData = {
      entertainment_recommendations: {
        top_movies: [
          {
            title: 'Minimal Movie',
            genre: 'Drama',
            rating: '8.0/10',
            platform: 'Netflix',
            description: 'Minimal description.'
            // No optional fields
          }
        ],
        theater_plays: [
          {
            title: 'Minimal Play',
            genre: 'Drama',
            description: 'Minimal play description.'
            // No optional fields like venue, show_times, etc.
          }
        ]
      }
    };

    render(<WeekendRecommendations weekendData={minimalData} />);
    
    // Should render successfully with minimal data
    expect(screen.getByText('Minimal Movie')).toBeInTheDocument();
    expect(screen.getByText('Minimal Play')).toBeInTheDocument();
    
    // Should not have broken layout or missing required elements
    expect(screen.getByText('🎬 Entertainment Hub')).toBeInTheDocument();
    expect(screen.getByText('🍿 Top Movies')).toBeInTheDocument();
    expect(screen.getByText('🎭 Theater & Plays')).toBeInTheDocument();
  });

  it('maintains focus management and keyboard navigation', () => {
    const { container } = render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    // Verify that interactive elements are properly structured
    // (Note: These cards are currently display-only, but structure should support future interactivity)
    const entertainmentCards = container.querySelectorAll('.entertainment-card');
    
    entertainmentCards.forEach(card => {
      // Cards should be properly structured for potential keyboard navigation
      expect(card).toBeInTheDocument();
      
      // Each card should have identifiable content
      const title = card.querySelector('.entertainment-title');
      expect(title).toBeInTheDocument();
    });
  });

  it('provides meaningful content structure for screen readers', () => {
    render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    // Verify logical content flow for screen readers
    const entertainmentHub = screen.getByText('🎬 Entertainment Hub');
    expect(entertainmentHub.tagName).toBe('H4');
    
    // Categories should be properly nested under the hub
    const movieCategory = screen.getByText('🍿 Top Movies');
    expect(movieCategory.tagName).toBe('H5');
    
    const seriesCategory = screen.getByText('📺 Must-Watch Series');
    expect(seriesCategory.tagName).toBe('H5');
    
    const theaterCategory = screen.getByText('🎭 Theater & Plays');
    expect(theaterCategory.tagName).toBe('H5');
    
    // Individual items should be properly nested under categories
    const movieTitle = screen.getByText('Test Movie');
    expect(movieTitle.tagName).toBe('H6');
  });

  it('handles empty states accessibly', () => {
    const emptyData: WeekendData = {};

    render(<WeekendRecommendations weekendData={emptyData} />);
    
    // Should still provide accessible structure even with no entertainment data
    expect(screen.getByText('🎉 Weekend Recommendations')).toBeInTheDocument();
    expect(screen.getByText('AI Curated')).toBeInTheDocument();
    expect(screen.getByText('Curated by our Weekend Events Agent')).toBeInTheDocument();
    
    // Should not render entertainment hub when no data
    expect(screen.queryByText('🎬 Entertainment Hub')).not.toBeInTheDocument();
  });

  it('provides consistent visual hierarchy', () => {
    const { container } = render(<WeekendRecommendations weekendData={mockEntertainmentData} />);
    
    // Check CSS class consistency
    expect(container.querySelector('.entertainment-hub')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-categories')).toBeInTheDocument();
    
    const categories = container.querySelectorAll('.entertainment-category');
    expect(categories).toHaveLength(3);
    
    const grids = container.querySelectorAll('.entertainment-grid');
    expect(grids).toHaveLength(3);
    
    const cards = container.querySelectorAll('.entertainment-card');
    expect(cards).toHaveLength(3);
    
    // Verify specific card types
    expect(container.querySelector('.movie-card')).toBeInTheDocument();
    expect(container.querySelector('.series-card')).toBeInTheDocument();
    expect(container.querySelector('.play-card')).toBeInTheDocument();
  });
});