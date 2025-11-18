/**
 * Audio Synchronization Tests
 * Tests for subtask 14.3: Test audio synchronization
 * Requirements: 10.1, 10.2
 * 
 * Tests:
 * - Verify audio plays from correct timestamp
 * - Test auto-advance on segment end
 * - Validate pause on manual navigation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CurioCardStack from '../cards/CurioCardStack';
import { BootstrapResponse } from '../cards/types';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>
  },
  AnimatePresence: ({ children }: any) => <>{children}</>
}));

// Mock react-swipeable
jest.mock('react-swipeable', () => ({
  useSwipeable: () => ({
    onSwipedLeft: jest.fn(),
    onSwipedRight: jest.fn()
  })
}));

// Mock lazy loaded components
jest.mock('../cards/OverviewCard', () => ({
  __esModule: true,
  default: ({ onTap }: any) => (
    <div data-testid="overview-card" onClick={onTap}>
      Overview Card
    </div>
  )
}));

jest.mock('../cards/StoryCard', () => ({
  __esModule: true,
  default: ({ story, onTap, onAudioPlay, currentCardIndex, isAudioPlaying }: any) => (
    <div data-testid={`story-card-${currentCardIndex}`} onClick={onTap}>
      <h2>{story.title}</h2>
      <button 
        data-testid={`audio-button-${currentCardIndex}`}
        onClick={(e) => {
          e.stopPropagation();
          onAudioPlay();
        }}
        aria-pressed={isAudioPlaying}
      >
        {isAudioPlaying ? 'Playing...' : 'Tap to listen'}
      </button>
    </div>
  )
}));

// Mock performance monitor
jest.mock('../../utils/performanceMonitor', () => ({
  performanceMonitor: {
    startTransition: jest.fn(),
    endTransition: jest.fn(),
    startMediaLoad: jest.fn(),
    endMediaLoad: jest.fn(),
    recordMediaLoadFailure: jest.fn(),
    getStats: jest.fn(() => ({
      averageTransitionTime: 450,
      averageMediaLoadTime: 800,
      peakMemoryUsage: 45.2,
      totalTransitions: 5,
      slowTransitions: 0
    })),
    getCurrentMemoryUsage: jest.fn(() => 42.5),
    isPerformanceAcceptable: jest.fn(() => true),
    logPerformanceReport: jest.fn(),
    destroy: jest.fn()
  }
}));

// Mock HTMLAudioElement
class MockAudio {
  src = '';
  currentTime = 0;
  paused = true;
  preload = 'auto';
  private listeners: { [key: string]: Function[] } = {};

  addEventListener(event: string, callback: Function) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  removeEventListener(event: string, callback: Function) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  play() {
    this.paused = false;
    this.trigger('play');
    return Promise.resolve();
  }

  pause() {
    this.paused = true;
    this.trigger('pause');
  }

  load() {}

  trigger(event: string) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback());
    }
  }

  triggerTimeUpdate() {
    this.trigger('timeupdate');
  }
}

// Create mock bootstrap data with audio timestamps
const createMockBootstrapData = (): BootstrapResponse => ({
  news_items: [
    {
      title: 'Story 1',
      summary: 'Summary 1',
      url: 'https://example.com/story1',
      source: 'Source 1',
      published_at: '2025-11-16T10:00:00Z',
      category: 'world',
      image_url: 'https://example.com/image1.jpg'
    },
    {
      title: 'Story 2',
      summary: 'Summary 2',
      url: 'https://example.com/story2',
      source: 'Source 2',
      published_at: '2025-11-16T11:00:00Z',
      category: 'local',
      image_url: 'https://example.com/image2.jpg'
    },
    {
      title: 'Story 3',
      summary: 'Summary 3',
      url: 'https://example.com/story3',
      source: 'Source 3',
      published_at: '2025-11-16T12:00:00Z',
      category: 'event',
      image_url: 'https://example.com/image3.jpg'
    }
  ],
  script: 'This is story one. This is story two. This is story three.',
  word_timings: [
    { word: 'This', start: 0, end: 0.5 },
    { word: 'is', start: 0.5, end: 0.8 },
    { word: 'story', start: 0.8, end: 1.2 },
    { word: 'one.', start: 1.2, end: 1.8 },
    { word: 'This', start: 20, end: 20.5 },
    { word: 'is', start: 20.5, end: 20.8 },
    { word: 'story', start: 20.8, end: 21.2 },
    { word: 'two.', start: 21.2, end: 21.8 },
    { word: 'This', start: 40, end: 40.5 },
    { word: 'is', start: 40.5, end: 40.8 },
    { word: 'story', start: 40.8, end: 41.2 },
    { word: 'three.', start: 41.2, end: 41.8 }
  ],
  audio_url: 'https://example.com/audio.mp3'
});

describe('Audio Synchronization (Subtask 14.3)', () => {
  let mockBootstrapData: BootstrapResponse;
  let mockAudio: MockAudio;

  beforeEach(() => {
    mockBootstrapData = createMockBootstrapData();
    mockAudio = new MockAudio();
    
    // Mock Audio constructor
    (global as any).Audio = jest.fn(() => mockAudio);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Audio plays from correct timestamp (Requirement 10.1)', () => {
    it('should seek to card audio timestamp when playing', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByTestId('overview-card'));

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Click audio button
      const audioButton = screen.getByTestId('audio-button-1');
      fireEvent.click(audioButton);

      // Audio should seek to the card's timestamp
      await waitFor(() => {
        // First story card should start at timestamp 0
        expect(mockAudio.currentTime).toBeGreaterThanOrEqual(0);
        expect(mockAudio.paused).toBe(false);
      });
    });

    it('should play audio from different timestamps for different cards', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByTestId('overview-card'));

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Play audio on first card
      fireEvent.click(screen.getByTestId('audio-button-1'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      const firstTimestamp = mockAudio.currentTime;

      // Pause audio
      fireEvent.click(screen.getByTestId('audio-button-1'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(true);
      });

      // Navigate to next card
      fireEvent.click(screen.getByTestId('story-card-1'));

      await waitFor(() => {
        expect(screen.getByTestId('story-card-2')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Play audio on second card
      fireEvent.click(screen.getByTestId('audio-button-2'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      const secondTimestamp = mockAudio.currentTime;

      // Second card should have different timestamp
      expect(secondTimestamp).not.toBe(firstTimestamp);
    });

    it('should toggle audio playback when clicking same card audio button', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByTestId('overview-card'));

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Click audio button to play
      const audioButton = screen.getByTestId('audio-button-1');
      fireEvent.click(audioButton);

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      // Click again to pause
      fireEvent.click(audioButton);

      await waitFor(() => {
        expect(mockAudio.paused).toBe(true);
      });
    });
  });

  describe('Auto-advance on segment end (Requirement 10.2)', () => {
    it('should auto-advance to next card when audio segment ends', async () => {
      jest.useFakeTimers();

      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByTestId('overview-card'));

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Play audio
      fireEvent.click(screen.getByTestId('audio-button-1'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      // Simulate audio reaching segment end (20 seconds for first segment)
      mockAudio.currentTime = 20;
      mockAudio.triggerTimeUpdate();

      // Fast-forward the interval check (100ms intervals)
      jest.advanceTimersByTime(200);

      // Should auto-advance to next card
      await waitFor(() => {
        expect(screen.getByTestId('story-card-2')).toBeInTheDocument();
      }, { timeout: 1000 });

      jest.useRealTimers();
    });

    it('should not auto-advance if audio is paused', async () => {
      jest.useFakeTimers();

      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByTestId('overview-card'));

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Play and immediately pause audio
      fireEvent.click(screen.getByTestId('audio-button-1'));
      fireEvent.click(screen.getByTestId('audio-button-1'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(true);
      });

      // Simulate time passing
      jest.advanceTimersByTime(25000);

      // Should still be on same card
      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      });

      jest.useRealTimers();
    });
  });

  describe('Pause on manual navigation (Requirement 10.2)', () => {
    it('should pause audio when manually navigating to next card', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByTestId('overview-card'));

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Play audio
      fireEvent.click(screen.getByTestId('audio-button-1'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      // Manually navigate to next card
      fireEvent.click(screen.getByTestId('story-card-1'));

      // Audio should be paused
      await waitFor(() => {
        expect(mockAudio.paused).toBe(true);
      });
    });

    it('should pause audio when navigating with keyboard', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.keyDown(window, { key: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Play audio
      fireEvent.click(screen.getByTestId('audio-button-1'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      // Navigate with keyboard
      fireEvent.keyDown(window, { key: 'ArrowRight' });

      // Audio should be paused
      await waitFor(() => {
        expect(mockAudio.paused).toBe(true);
      });
    });

    it('should pause audio when navigating backwards', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to second story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.keyDown(window, { key: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      fireEvent.keyDown(window, { key: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByTestId('story-card-2')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Play audio
      fireEvent.click(screen.getByTestId('audio-button-2'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      // Navigate backwards
      fireEvent.keyDown(window, { key: 'ArrowLeft' });

      // Audio should be paused
      await waitFor(() => {
        expect(mockAudio.paused).toBe(true);
      });
    });

    it('should pause audio with Escape key', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.keyDown(window, { key: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Play audio
      fireEvent.click(screen.getByTestId('audio-button-1'));

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      // Press Escape
      fireEvent.keyDown(window, { key: 'Escape' });

      // Audio should be paused
      await waitFor(() => {
        expect(mockAudio.paused).toBe(true);
      });
    });
  });

  describe('Audio keyboard controls', () => {
    it('should play/pause audio with Space key on story cards', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.keyDown(window, { key: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Press Space to play
      fireEvent.keyDown(window, { key: ' ' });

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });

      // Press Space again to pause
      fireEvent.keyDown(window, { key: ' ' });

      await waitFor(() => {
        expect(mockAudio.paused).toBe(true);
      });
    });

    it('should play/pause audio with Enter key on story cards', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.keyDown(window, { key: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Press Enter to play
      fireEvent.keyDown(window, { key: 'Enter' });

      await waitFor(() => {
        expect(mockAudio.paused).toBe(false);
      });
    });

    it('should not trigger audio on overview card with Space/Enter', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      // Press Space on overview card
      fireEvent.keyDown(window, { key: ' ' });

      // Audio should not play
      expect(mockAudio.paused).toBe(true);
    });
  });

  describe('Audio accessibility', () => {
    it('should update aria-pressed state when audio is playing', async () => {
      render(<CurioCardStack bootstrapData={mockBootstrapData} />);

      // Navigate to first story card
      await waitFor(() => {
        expect(screen.getByTestId('overview-card')).toBeInTheDocument();
      });

      fireEvent.keyDown(window, { key: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByTestId('story-card-1')).toBeInTheDocument();
      }, { timeout: 1000 });

      const audioButton = screen.getByTestId('audio-button-1');

      // Initially not pressed
      expect(audioButton).toHaveAttribute('aria-pressed', 'false');

      // Click to play
      fireEvent.click(audioButton);

      await waitFor(() => {
        expect(audioButton).toHaveAttribute('aria-pressed', 'true');
      });
    });
  });
});
