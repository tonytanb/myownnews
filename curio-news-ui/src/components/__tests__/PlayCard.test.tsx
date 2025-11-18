import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import PlayCard from '../PlayCard';
import { TheaterPlay } from '../WeekendRecommendations';

describe('PlayCard', () => {
  const mockPlay: TheaterPlay = {
    title: 'Hamilton',
    genre: 'Musical',
    venue: 'Richard Rodgers Theatre',
    city: 'New York',
    description: 'The story of American founding father Alexander Hamilton.',
    show_times: 'Tue-Sun 8PM, Wed & Sat 2PM',
    ticket_info: 'From $79',
    rating: '9.5/10'
  };

  it('renders play card with all information', () => {
    render(<PlayCard play={mockPlay} />);
    
    expect(screen.getByText('Hamilton')).toBeInTheDocument();
    expect(screen.getByText('Musical')).toBeInTheDocument();
    expect(screen.getByText('📍 Richard Rodgers Theatre')).toBeInTheDocument();
    expect(screen.getByText('New York')).toBeInTheDocument();
    expect(screen.getByText(/The story of American founding father/)).toBeInTheDocument();
    expect(screen.getByText('🕐 Tue-Sun 8PM, Wed & Sat 2PM')).toBeInTheDocument();
    expect(screen.getByText('🎫 From $79')).toBeInTheDocument();
    expect(screen.getByText('9.5/10')).toBeInTheDocument();
  });

  it('renders play card with minimal information', () => {
    const minimalPlay: TheaterPlay = {
      title: 'Simple Play',
      genre: 'Drama',
      description: 'A simple play description.'
    };

    render(<PlayCard play={minimalPlay} />);
    
    expect(screen.getByText('Simple Play')).toBeInTheDocument();
    expect(screen.getByText('Drama')).toBeInTheDocument();
    expect(screen.getByText('A simple play description.')).toBeInTheDocument();
    
    // Optional fields should not be present
    expect(screen.queryByText(/📍/)).not.toBeInTheDocument();
    expect(screen.queryByText(/🕐/)).not.toBeInTheDocument();
    expect(screen.queryByText(/🎫/)).not.toBeInTheDocument();
    expect(screen.queryByText(/\/10/)).not.toBeInTheDocument();
  });

  it('renders play card without rating', () => {
    const playWithoutRating: TheaterPlay = {
      title: 'Local Play',
      genre: 'Comedy',
      venue: 'Community Theater',
      description: 'A local comedy play.'
    };

    render(<PlayCard play={playWithoutRating} />);
    
    expect(screen.getByText('Local Play')).toBeInTheDocument();
    expect(screen.getByText('📍 Community Theater')).toBeInTheDocument();
    
    // Rating badge should not be present
    const { container } = render(<PlayCard play={playWithoutRating} />);
    expect(container.querySelector('.rating-badge')).not.toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    const { container } = render(<PlayCard play={mockPlay} />);
    
    expect(container.querySelector('.entertainment-card')).toBeInTheDocument();
    expect(container.querySelector('.play-card')).toBeInTheDocument();
    expect(container.querySelector('.card-header')).toBeInTheDocument();
    expect(container.querySelector('.rating-badge')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-title')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-meta')).toBeInTheDocument();
    expect(container.querySelector('.entertainment-description')).toBeInTheDocument();
    expect(container.querySelector('.show-info')).toBeInTheDocument();
    expect(container.querySelector('.ticket-info')).toBeInTheDocument();
  });

  it('conditionally renders show times and ticket info', () => {
    const playWithShowTimes: TheaterPlay = {
      title: 'Show Times Only',
      genre: 'Drama',
      description: 'Play with show times only.',
      show_times: 'Daily 7PM'
    };

    const { rerender } = render(<PlayCard play={playWithShowTimes} />);
    
    expect(screen.getByText('🕐 Daily 7PM')).toBeInTheDocument();
    expect(screen.queryByText(/🎫/)).not.toBeInTheDocument();

    const playWithTicketInfo: TheaterPlay = {
      title: 'Ticket Info Only',
      genre: 'Comedy',
      description: 'Play with ticket info only.',
      ticket_info: 'Sold Out'
    };

    rerender(<PlayCard play={playWithTicketInfo} />);
    
    expect(screen.getByText('🎫 Sold Out')).toBeInTheDocument();
    expect(screen.queryByText(/🕐/)).not.toBeInTheDocument();
  });

  it('handles venue without city', () => {
    const playVenueOnly: TheaterPlay = {
      title: 'Venue Only Play',
      genre: 'Musical',
      venue: 'Local Theater',
      description: 'Play with venue but no city.'
    };

    render(<PlayCard play={playVenueOnly} />);
    
    expect(screen.getByText('📍 Local Theater')).toBeInTheDocument();
    expect(screen.queryByText('New York')).not.toBeInTheDocument();
  });
});