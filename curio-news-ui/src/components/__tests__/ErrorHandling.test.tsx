import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import FavoriteStory from '../FavoriteStory';
import WeekendRecommendations from '../WeekendRecommendations';
import MediaGallery from '../MediaGallery';

describe('Error Handling Components', () => {
  const mockRetry = jest.fn();

  beforeEach(() => {
    mockRetry.mockClear();
  });

  describe('FavoriteStory Error Handling', () => {
    it('displays error message and retry button', () => {
      render(
        <FavoriteStory
          error="Test error message"
          onRetry={mockRetry}
          retryAttempt={1}
          maxRetries={3}
        />
      );

      expect(screen.getByText(/Content Generation Failed/)).toBeInTheDocument();
      expect(screen.getByText(/Test error message/)).toBeInTheDocument();
      expect(screen.getByText(/Retry Favorite Story/)).toBeInTheDocument();
    });

    it('calls retry function when retry button is clicked', () => {
      render(
        <FavoriteStory
          error="Test error"
          onRetry={mockRetry}
          retryAttempt={1}
          maxRetries={3}
        />
      );

      const retryButton = screen.getByText(/Retry Favorite Story/);
      fireEvent.click(retryButton);
      
      expect(mockRetry).toHaveBeenCalledTimes(1);
    });

    it('shows max retries reached message when retries exhausted', () => {
      render(
        <FavoriteStory
          error="Test error"
          onRetry={mockRetry}
          retryAttempt={3}
          maxRetries={3}
        />
      );

      expect(screen.getByText(/Maximum retry attempts reached/)).toBeInTheDocument();
      expect(screen.queryByText(/Retry Favorite Story/)).not.toBeInTheDocument();
    });
  });

  describe('WeekendRecommendations Error Handling', () => {
    it('displays error message and retry button', () => {
      render(
        <WeekendRecommendations
          error="Weekend error"
          onRetry={mockRetry}
          retryAttempt={0}
          maxRetries={3}
        />
      );

      expect(screen.getByText(/Content Generation Failed/)).toBeInTheDocument();
      expect(screen.getByText(/Weekend error/)).toBeInTheDocument();
      expect(screen.getByText(/Retry Weekend Recommendations/)).toBeInTheDocument();
    });
  });

  describe('MediaGallery Error Handling', () => {
    it('displays error message and retry button', () => {
      render(
        <MediaGallery
          error="Media error"
          onRetry={mockRetry}
          retryAttempt={0}
          maxRetries={3}
        />
      );

      expect(screen.getByText(/Content Generation Failed/)).toBeInTheDocument();
      expect(screen.getByText(/Media error/)).toBeInTheDocument();
      expect(screen.getByText(/Retry Visual Enhancements/)).toBeInTheDocument();
    });
  });
});