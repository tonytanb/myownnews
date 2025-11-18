/**
 * CategoryTag Component
 * Displays a visual badge indicating the story category with gradient background and icon
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
 */

import React from 'react';
import { Heart, Globe, MapPin, Calendar, Film, Music, Book } from 'lucide-react';
import { CategoryTagProps } from './types';
import { categoryConfig } from '../../utils/categoryMapping';
import './CategoryTag.css';

/**
 * Map icon names to Lucide icon components
 */
const iconMap = {
  Heart,
  Globe,
  MapPin,
  Calendar,
  Film,
  Music,
  Book
};

/**
 * CategoryTag component
 * Renders a gradient badge with icon and label in the top-left corner of story cards
 * 
 * @param category - The category type to display
 */
export const CategoryTag: React.FC<CategoryTagProps> = ({ category }) => {
  const config = categoryConfig[category];
  const IconComponent = iconMap[config.icon as keyof typeof iconMap];

  return (
    <div 
      className={`category-tag bg-gradient-to-r ${config.gradient}`}
      role="img"
      aria-label={`${config.label} category`}
    >
      <IconComponent 
        className="category-tag__icon" 
        size={16}
        strokeWidth={2.5}
        aria-hidden="true"
      />
      <span className="category-tag__label">
        {config.label}
      </span>
    </div>
  );
};

export default CategoryTag;
