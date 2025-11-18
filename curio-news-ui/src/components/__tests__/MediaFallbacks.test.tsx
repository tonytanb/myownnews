/**
 * Media Loading and Fallbacks Tests
 * Tests for subtask 14.2: Test media loading and fallbacks
 * Requirements: 4.5, 11.5
 * 
 * Tests:
 * - Simulate video load failures
 * - Verify Unsplash fallback works
 * - Test placeholder generation
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import BackgroundMedia from '../cards/BackgroundMedia';

// Mock performance monitor
jest.mock('../../utils/performanceMonitor', () => ({
  performanceMonitor: {
    startMediaLoad: jest.fn(),
    endMediaLoad: jest.fn(),
    recordMediaLoadFailure: jest.fn()
  }
}));

// Mock media optimizer
jest.mock('../../utils/mediaOptimizer', () => ({
  getOptimizedImageUrl: (url: string) => url,
  getOptimizedVideoUrl: (url: string) => url,
  getBestImageFormat: () => 'webp',
  getResponsiveImageSrcSet: (url: string) => url
}));

describe('Media Loading and Fallbacks (Subtask 14.2)', () => {
  describe('Video load failures (Requirement 4.5)', () => {
    it('should fallback to image when video fails to load', async () => {
      const mockOnError = jest.fn();
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/video.mp4"
          mediaType="video"
          fallbackImage="https://example.com/fallback.jpg"
          alt="Test video"
          category="world"
          onError={mockOnError}
        />
      );

      // Wait for video element to render
      await waitFor(() => {
        const video = container.querySelector('video');
        expect(video).toBeInTheDocument();
      });

      // Simulate video load error
      const video = container.querySelector('video');
      if (video) {
        fireEvent.error(video);
      }

      // Should fallback to image
      await waitFor(() => {
        const img = container.querySelector('img');
        expect(img).toBeInTheDocument();
        expect(img).toHaveAttribute('src', 'https://example.com/fallback.jpg');
      });

      // Should call onError callback with 'video' error type
      expect(mockOnError).toHaveBeenCalledWith('video');
    });

    it('should display loading state while video loads', async () => {
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/video.mp4"
          mediaType="video"
          fallbackImage="https://example.com/fallback.jpg"
          alt="Test video"
          category="world"
        />
      );

      // Should show loading spinner initially
      await waitFor(() => {
        expect(screen.getByRole('status', { name: /loading media/i })).toBeInTheDocument();
      });
    });

    it('should hide loading state after video loads', async () => {
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/video.mp4"
          mediaType="video"
          fallbackImage="https://example.com/fallback.jpg"
          alt="Test video"
          category="world"
        />
      );

      // Wait for video element
      await waitFor(() => {
        const video = container.querySelector('video');
        expect(video).toBeInTheDocument();
      });

      // Simulate video loaded
      const video = container.querySelector('video');
      if (video) {
        fireEvent.loadedData(video);
      }

      // Loading state should be hidden
      await waitFor(() => {
        expect(screen.queryByRole('status', { name: /loading media/i })).not.toBeInTheDocument();
      });
    });
  });

  describe('Unsplash fallback (Requirement 11.5)', () => {
    it('should fallback to Unsplash when image fails to load', async () => {
      const mockOnError = jest.fn();
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/broken-image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Test image"
          category="world"
          onError={mockOnError}
        />
      );

      // Wait for image element
      await waitFor(() => {
        const img = container.querySelector('img');
        expect(img).toBeInTheDocument();
      });

      // Simulate image load error
      const img = container.querySelector('img');
      if (img) {
        fireEvent.error(img);
      }

      // Should fallback to Unsplash URL
      await waitFor(() => {
        const newImg = container.querySelector('img');
        expect(newImg).toBeInTheDocument();
        expect(newImg?.getAttribute('src')).toContain('unsplash.com');
      });

      // Should call onError callback with 'image' error type
      expect(mockOnError).toHaveBeenCalledWith('image');
    });

    it('should generate Unsplash URL with category keywords', async () => {
      const mockOnError = jest.fn();
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/broken-image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Test image"
          category="movie"
          onError={mockOnError}
        />
      );

      // Wait for image element
      await waitFor(() => {
        const img = container.querySelector('img');
        expect(img).toBeInTheDocument();
      });

      // Simulate image load error
      const img = container.querySelector('img');
      if (img) {
        fireEvent.error(img);
      }

      // Should use category-specific keywords in Unsplash URL
      await waitFor(() => {
        const newImg = container.querySelector('img');
        const src = newImg?.getAttribute('src') || '';
        expect(src).toContain('unsplash.com');
        // URL should contain category-related keywords
        expect(src).toMatch(/cinema|film|movie/);
      });
    });

    it('should use deterministic hash for consistent Unsplash images', async () => {
      const mockOnError = jest.fn();
      const { container: container1 } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/broken-image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Same alt text"
          category="world"
          onError={mockOnError}
        />
      );

      // Trigger error to get Unsplash URL
      await waitFor(() => {
        const img = container1.querySelector('img');
        expect(img).toBeInTheDocument();
      });

      const img1 = container1.querySelector('img');
      if (img1) {
        fireEvent.error(img1);
      }

      await waitFor(() => {
        const newImg = container1.querySelector('img');
        expect(newImg?.getAttribute('src')).toContain('unsplash.com');
      });

      const url1 = container1.querySelector('img')?.getAttribute('src');

      // Render again with same alt text
      const { container: container2 } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/broken-image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Same alt text"
          category="world"
          onError={mockOnError}
        />
      );

      await waitFor(() => {
        const img = container2.querySelector('img');
        expect(img).toBeInTheDocument();
      });

      const img2 = container2.querySelector('img');
      if (img2) {
        fireEvent.error(img2);
      }

      await waitFor(() => {
        const newImg = container2.querySelector('img');
        expect(newImg?.getAttribute('src')).toContain('unsplash.com');
      });

      const url2 = container2.querySelector('img')?.getAttribute('src');

      // URLs should be the same (deterministic)
      expect(url1).toBe(url2);
    });
  });

  describe('Placeholder generation (Requirement 11.5)', () => {
    it('should fallback to placeholder when Unsplash fails', async () => {
      const mockOnError = jest.fn();
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/broken-image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Test image"
          category="world"
          onError={mockOnError}
        />
      );

      // Wait for image element
      await waitFor(() => {
        const img = container.querySelector('img');
        expect(img).toBeInTheDocument();
      });

      // Simulate first error (original image)
      let img = container.querySelector('img');
      if (img) {
        fireEvent.error(img);
      }

      // Wait for Unsplash fallback
      await waitFor(() => {
        const newImg = container.querySelector('img');
        expect(newImg?.getAttribute('src')).toContain('unsplash.com');
      });

      // Simulate second error (Unsplash)
      img = container.querySelector('img');
      if (img) {
        fireEvent.error(img);
      }

      // Should fallback to placeholder
      await waitFor(() => {
        const finalImg = container.querySelector('img');
        expect(finalImg?.getAttribute('src')).toContain('placeholder.com');
      });

      // Should call onError callback with 'unsplash' error type
      expect(mockOnError).toHaveBeenCalledWith('unsplash');
    });

    it('should generate placeholder with category-specific colors', async () => {
      const mockOnError = jest.fn();
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/broken-image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Test image"
          category="favorite"
          onError={mockOnError}
        />
      );

      // Trigger errors to reach placeholder
      await waitFor(() => {
        const img = container.querySelector('img');
        expect(img).toBeInTheDocument();
      });

      // First error
      let img = container.querySelector('img');
      if (img) {
        fireEvent.error(img);
      }

      await waitFor(() => {
        const newImg = container.querySelector('img');
        expect(newImg?.getAttribute('src')).toContain('unsplash.com');
      });

      // Second error
      img = container.querySelector('img');
      if (img) {
        fireEvent.error(img);
      }

      // Should use favorite category colors (pink/rose)
      await waitFor(() => {
        const finalImg = container.querySelector('img');
        const src = finalImg?.getAttribute('src') || '';
        expect(src).toContain('placeholder.com');
        expect(src).toMatch(/ec4899|f43f5e/); // Pink/rose colors
      });
    });

    it('should generate placeholder with category emoji', async () => {
      const mockOnError = jest.fn();
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/broken-image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Test image"
          category="movie"
          onError={mockOnError}
        />
      );

      // Trigger errors to reach placeholder
      await waitFor(() => {
        const img = container.querySelector('img');
        expect(img).toBeInTheDocument();
      });

      // First error
      let img = container.querySelector('img');
      if (img) {
        fireEvent.error(img);
      }

      await waitFor(() => {
        const newImg = container.querySelector('img');
        expect(newImg?.getAttribute('src')).toContain('unsplash.com');
      });

      // Second error
      img = container.querySelector('img');
      if (img) {
        fireEvent.error(img);
      }

      // Should include movie emoji in placeholder
      await waitFor(() => {
        const finalImg = container.querySelector('img');
        const src = finalImg?.getAttribute('src') || '';
        expect(src).toContain('placeholder.com');
        expect(src).toContain(encodeURIComponent('🎬'));
      });
    });
  });

  describe('Error handling limits', () => {
    it('should stop retrying after max retries', async () => {
      const mockOnError = jest.fn();
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/broken-image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Test image"
          category="world"
          onError={mockOnError}
        />
      );

      // Trigger multiple errors
      for (let i = 0; i < 5; i++) {
        await waitFor(() => {
          const img = container.querySelector('img');
          expect(img).toBeInTheDocument();
        });

        const img = container.querySelector('img');
        if (img) {
          fireEvent.error(img);
        }

        // Small delay between errors
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Should have stopped retrying (max 3 retries)
      // onError should be called max 3 times
      expect(mockOnError).toHaveBeenCalledTimes(3);
    });
  });

  describe('Media accessibility', () => {
    it('should have proper alt text for images', async () => {
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Breaking news story about climate"
          category="world"
        />
      );

      await waitFor(() => {
        const img = container.querySelector('img');
        expect(img).toBeInTheDocument();
        expect(img).toHaveAttribute('alt', 'Breaking news story about climate');
      });
    });

    it('should have proper aria-label for videos', async () => {
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/video.mp4"
          mediaType="video"
          fallbackImage=""
          alt="Breaking news video about climate"
          category="world"
        />
      );

      await waitFor(() => {
        const video = container.querySelector('video');
        expect(video).toBeInTheDocument();
        expect(video).toHaveAttribute('aria-label', 'Background video: Breaking news video about climate');
      });
    });

    it('should have role="img" for media elements', async () => {
      const { container } = render(
        <BackgroundMedia
          mediaUrl="https://example.com/image.jpg"
          mediaType="image"
          fallbackImage=""
          alt="Test image"
          category="world"
        />
      );

      await waitFor(() => {
        const img = container.querySelector('img');
        expect(img).toBeInTheDocument();
        expect(img).toHaveAttribute('role', 'img');
      });
    });
  });
});
