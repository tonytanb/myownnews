import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import OverviewCard from '../OverviewCard';
import { OverviewCardProps } from '../types';

describe('OverviewCard', () => {
  const mockProps: OverviewCardProps = {
    date: '2025-11-16',
    highlights: [
      '🌍 Breaking: Global climate summit reaches agreement',
      '💼 Tech sector sees major innovation',
      '🎬 New blockbuster breaks box office records',
      '🎵 Music festival announces lineup',
      '📚 Bestselling author releases new book'
    ],
    totalStories: 8,
    backgroundImage: 'https://example.com/background.jpg',
    onTap: jest.fn()
  };

  it('renders the title correctly', () => {
    render(<OverviewCard {...mockProps} />);
    expect(screen.getByText('Today in Curio 🪄')).toBeInTheDocument();
  });

  it('formats and displays the date in long format', () => {
    render(<OverviewCard {...mockProps} />);
    // Date format depends on timezone, so just check it contains November and 2025
    expect(screen.getByText(/November.*2025/)).toBeInTheDocument();
  });

  it('displays the story count', () => {
    render(<OverviewCard {...mockProps} />);
    expect(screen.getByText('8 stories curated for you')).toBeInTheDocument();
  });

  it('displays highlights (max 6)', () => {
    render(<OverviewCard {...mockProps} />);
    expect(screen.getByText(/Breaking: Global climate summit/)).toBeInTheDocument();
    expect(screen.getByText(/Tech sector sees major innovation/)).toBeInTheDocument();
  });

  it('displays the call to action text', () => {
    render(<OverviewCard {...mockProps} />);
    expect(screen.getByText('Tap to begin')).toBeInTheDocument();
    expect(screen.getByText('→')).toBeInTheDocument();
  });

  it('displays the Curio watermark', () => {
    render(<OverviewCard {...mockProps} />);
    expect(screen.getByText('curio')).toBeInTheDocument();
  });

  it('calls onTap when clicked', () => {
    render(<OverviewCard {...mockProps} />);
    const card = screen.getByText('Today in Curio 🪄').closest('.overview-card');
    fireEvent.click(card!);
    expect(mockProps.onTap).toHaveBeenCalledTimes(1);
  });

  it('handles singular story count', () => {
    const singleStoryProps = { ...mockProps, totalStories: 1 };
    render(<OverviewCard {...singleStoryProps} />);
    expect(screen.getByText('1 story curated for you')).toBeInTheDocument();
  });

  it('limits highlights to 6 items', () => {
    const manyHighlights = [
      '🌍 Highlight 1',
      '💼 Highlight 2',
      '🎬 Highlight 3',
      '🎵 Highlight 4',
      '📚 Highlight 5',
      '⚽ Highlight 6',
      '🎨 Highlight 7',
      '🔬 Highlight 8'
    ];
    const propsWithMany = { ...mockProps, highlights: manyHighlights };
    render(<OverviewCard {...propsWithMany} />);
    
    // Should show first 6
    expect(screen.getByText(/Highlight 1/)).toBeInTheDocument();
    expect(screen.getByText(/Highlight 6/)).toBeInTheDocument();
    
    // Should not show 7th and 8th
    expect(screen.queryByText(/Highlight 7/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Highlight 8/)).not.toBeInTheDocument();
  });
});
