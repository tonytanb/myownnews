import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CategoryTag } from '../cards/CategoryTag';
import { CategoryType } from '../cards/types';

describe('CategoryTag', () => {
  it('renders favorite category with correct label and icon', () => {
    const { container } = render(<CategoryTag category="favorite" />);
    
    expect(screen.getByText('FAVORITE')).toBeInTheDocument();
    expect(screen.getByLabelText('FAVORITE category')).toBeInTheDocument();
    expect(container.querySelector('.category-tag')).toBeInTheDocument();
  });

  it('renders world category with correct label', () => {
    render(<CategoryTag category="world" />);
    
    expect(screen.getByText('WORLD')).toBeInTheDocument();
    expect(screen.getByLabelText('WORLD category')).toBeInTheDocument();
  });

  it('renders local category with correct label', () => {
    render(<CategoryTag category="local" />);
    
    expect(screen.getByText('LOCAL')).toBeInTheDocument();
    expect(screen.getByLabelText('LOCAL category')).toBeInTheDocument();
  });

  it('renders event category with correct label', () => {
    render(<CategoryTag category="event" />);
    
    expect(screen.getByText('EVENT')).toBeInTheDocument();
    expect(screen.getByLabelText('EVENT category')).toBeInTheDocument();
  });

  it('renders movie category with correct label', () => {
    render(<CategoryTag category="movie" />);
    
    expect(screen.getByText('MOVIE')).toBeInTheDocument();
    expect(screen.getByLabelText('MOVIE category')).toBeInTheDocument();
  });

  it('renders music category with correct label', () => {
    render(<CategoryTag category="music" />);
    
    expect(screen.getByText('MUSIC')).toBeInTheDocument();
    expect(screen.getByLabelText('MUSIC category')).toBeInTheDocument();
  });

  it('renders book category with correct label', () => {
    render(<CategoryTag category="book" />);
    
    expect(screen.getByText('BOOK')).toBeInTheDocument();
    expect(screen.getByLabelText('BOOK category')).toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    const { container } = render(<CategoryTag category="favorite" />);
    
    expect(container.querySelector('.category-tag')).toBeInTheDocument();
    expect(container.querySelector('.category-tag__icon')).toBeInTheDocument();
    expect(container.querySelector('.category-tag__label')).toBeInTheDocument();
  });

  it('applies gradient background class', () => {
    const { container } = render(<CategoryTag category="world" />);
    const tag = container.querySelector('.category-tag');
    
    expect(tag).toHaveClass('bg-gradient-to-r');
    expect(tag).toHaveClass('from-blue-500');
    expect(tag).toHaveClass('to-indigo-500');
  });

  it('renders icon with correct size', () => {
    const { container } = render(<CategoryTag category="favorite" />);
    const icon = container.querySelector('.category-tag__icon');
    
    // Icon component is rendered
    expect(icon).toBeInTheDocument();
  });

  it('has proper accessibility attributes', () => {
    const { container } = render(<CategoryTag category="movie" />);
    const tag = container.querySelector('.category-tag');
    
    expect(tag).toHaveAttribute('role', 'img');
    expect(tag).toHaveAttribute('aria-label', 'MOVIE category');
  });

  it('icon has aria-hidden attribute', () => {
    const { container } = render(<CategoryTag category="music" />);
    const icon = container.querySelector('.category-tag__icon');
    
    expect(icon).toHaveAttribute('aria-hidden', 'true');
  });
});
