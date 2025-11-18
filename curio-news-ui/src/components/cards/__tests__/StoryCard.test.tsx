/**
 * StoryCard Component Tests
 * Tests for the StoryCard component rendering and interactions
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { StoryCard } from '../StoryCard';
import { NewsItem, CategoryType, MediaType } from '../types';

describe('StoryCard', () => {
  const mockStory: NewsItem = {
    title: 'Test News Story',
    summary: 'This is a test summary for the news story.',
    url: 'https://example.com/story',
    source: 'Test Source',
    published_at: '2025-11-16T12:00:00Z',
    category: 'world',
    image_url: 'https://example.com/image.jpg'
  };

  const defaultProps = {
    story: mockStory,
    categoryType: 'world' as CategoryType,
    scriptSegment: 'This is the script segment for the story.',
    estimatedDuration: 25,
    mediaUrl: 'https://example.com/video.mp4',
    mediaType: 'video' as MediaType,
    onAudioPlay: jest.fn(),
    onTap: jest.fn(),
    currentCardIndex: 0,
    totalCards: 5
  };

  it('renders the story card with all elements', () => {
    render(<StoryCard {...defaultProps} />);

    // Check for title
    expect(screen.getByText('Test News Story')).toBeInTheDocument();

    // Check for summary
    expect(screen.getByText('This is a test summary for the news story.')).toBeInTheDocument();

    // Check for watermark
    expect(screen.getByText('curio')).toBeInTheDocument();

    // Check for audio button
    expect(screen.getByLabelText('Play audio narration')).toBeInTheDocument();
    expect(screen.getByText('Tap to listen')).toBeInTheDocument();
  });

  it('renders navigation dots correctly', () => {
    render(<StoryCard {...defaultProps} />);

    // Should render 5 dots (totalCards = 5)
    const dots = screen.getAllByLabelText(/Card \d+ of 5/);
    expect(dots).toHaveLength(5);

    // First dot should be active
    expect(dots[0]).toHaveClass('story-card__dot--active');
    expect(dots[1]).not.toHaveClass('story-card__dot--active');
  });

  it('calls onTap when card is clicked', () => {
    const onTap = jest.fn();
    render(<StoryCard {...defaultProps} onTap={onTap} />);

    const card = screen.getByRole('article');
    fireEvent.click(card);

    expect(onTap).toHaveBeenCalledTimes(1);
  });

  it('calls onAudioPlay when audio button is clicked', () => {
    const onAudioPlay = jest.fn();
    render(<StoryCard {...defaultProps} onAudioPlay={onAudioPlay} />);

    const audioButton = screen.getByLabelText('Play audio narration');
    fireEvent.click(audioButton);

    expect(onAudioPlay).toHaveBeenCalledTimes(1);
  });

  it('prevents card tap when audio button is clicked', () => {
    const onTap = jest.fn();
    const onAudioPlay = jest.fn();
    render(<StoryCard {...defaultProps} onTap={onTap} onAudioPlay={onAudioPlay} />);

    const audioButton = screen.getByLabelText('Play audio narration');
    fireEvent.click(audioButton);

    // onAudioPlay should be called, but onTap should not
    expect(onAudioPlay).toHaveBeenCalledTimes(1);
    expect(onTap).not.toHaveBeenCalled();
  });

  it('renders with different category types', () => {
    const { rerender } = render(<StoryCard {...defaultProps} categoryType="favorite" />);
    expect(screen.getByLabelText('FAVORITE category')).toBeInTheDocument();

    rerender(<StoryCard {...defaultProps} categoryType="local" />);
    expect(screen.getByLabelText('LOCAL category')).toBeInTheDocument();

    rerender(<StoryCard {...defaultProps} categoryType="movie" />);
    expect(screen.getByLabelText('MOVIE category')).toBeInTheDocument();
  });

  it('renders with correct accessibility attributes', () => {
    render(<StoryCard {...defaultProps} />);

    const card = screen.getByRole('article');
    expect(card).toHaveAttribute('aria-label', 'Story: Test News Story');

    const audioButton = screen.getByRole('button');
    expect(audioButton).toHaveAttribute('aria-label', 'Play audio narration');
  });

  it('highlights the correct navigation dot', () => {
    const { rerender } = render(
      <StoryCard {...defaultProps} currentCardIndex={0} totalCards={3} />
    );

    let dots = screen.getAllByLabelText(/Card \d+ of 3/);
    expect(dots[0]).toHaveClass('story-card__dot--active');
    expect(dots[1]).not.toHaveClass('story-card__dot--active');
    expect(dots[2]).not.toHaveClass('story-card__dot--active');

    // Change to second card
    rerender(<StoryCard {...defaultProps} currentCardIndex={1} totalCards={3} />);

    dots = screen.getAllByLabelText(/Card \d+ of 3/);
    expect(dots[0]).not.toHaveClass('story-card__dot--active');
    expect(dots[1]).toHaveClass('story-card__dot--active');
    expect(dots[2]).not.toHaveClass('story-card__dot--active');
  });
});
