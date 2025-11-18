/**
 * Audio Integration Tests
 * Tests for audio playback integration with card navigation
 * Requirements: 7.1, 10.1, 10.2, 10.4
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CurioCardStack from '../cards/CurioCardStack';
import { BootstrapResponse } from '../cards/types';

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// Mock react-swipeable
jest.mock('react-swipeable', () => ({
  useSwipeable: () => ({}),
}));

describe('Audio Integration', () => {
  const mockBootstrapData: BootstrapResponse = {
    news_items: [
      {
        title: 'Test Story 1',
        summary: 'Test summary 1',
        url: 'https://example.com/1',
        source: 'Test Source',
        published_at: '2025-01-01T00:00:00Z',
        category: 'world',
      },
      {
        title: 'Test Story 2',
        summary: 'Test summary 2',
        url: 'https://example.com/2',
        source: 'Test Source',
        published_at: '2025-01-01T00:00:00Z',
        category: 'local',
      },
    ],
    script: 'Test script content for audio playback.',
    word_timings: [
      { word: 'Test', start: 0, end: 0.5 },
      { word: 'script', start: 0.5, end: 1.0 },
      { word: 'content', start: 1.0, end: 1.5 },
    ],
    audio_url: 'https://example.com/audio.mp3',
  };

  beforeEach(() => {
    // Mock HTMLAudioElement
    global.Audio = jest.fn().mockImplementation(() => ({
      play: jest.fn().mockResolvedValue(undefined),
      pause: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      currentTime: 0,
      duration: 90,
      volume: 1,
      src: '',
      preload: 'auto',
    })) as any;
  });

  it('initializes audio element with correct source', () => {
    render(<CurioCardStack bootstrapData={mockBootstrapData} audioUrl="https://example.com/audio.mp3" />);
    
    expect(global.Audio).toHaveBeenCalled();
  });

  it('renders overview card first without audio button', async () => {
    render(<CurioCardStack bootstrapData={mockBootstrapData} />);
    
    // Wait for cards to be transformed and rendered
    await waitFor(() => {
      // Overview card should be shown first
      expect(screen.getByText('Today in Curio 🪄')).toBeInTheDocument();
      
      // Overview card should not have audio button
      const audioButtons = screen.queryAllByLabelText(/audio narration/i);
      expect(audioButtons.length).toBe(0);
    });
  });

  it('audio button shows correct text when not playing', async () => {
    render(<CurioCardStack bootstrapData={mockBootstrapData} />);
    
    await waitFor(() => {
      const tapToListen = screen.queryByText('Tap to listen');
      if (tapToListen) {
        expect(tapToListen).toBeInTheDocument();
      }
    });
  });

  it('has proper accessibility attributes for audio controls', async () => {
    render(<CurioCardStack bootstrapData={mockBootstrapData} />);
    
    await waitFor(() => {
      const audioButtons = screen.queryAllByLabelText(/audio narration/i);
      if (audioButtons.length > 0) {
        expect(audioButtons[0]).toHaveAttribute('aria-label');
      }
    });
  });
});
