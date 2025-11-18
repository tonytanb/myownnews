# Entertainment Recommendations Fix Design Document

## Overview

This design replaces the "Cultural Pulse" section in the WeekendRecommendations component with a comprehensive "Top Movies/Series/Plays" recommendations section. The change transforms social media insights into actionable entertainment suggestions while maintaining the existing visual design language.

## Architecture

### Current Structure Analysis

The WeekendRecommendations component currently has:
- Books section (BookTok Trending)
- Movies section (Streaming Picks) 
- Events section (Local Events)
- Cultural Pulse section (Social media insights)

### Proposed Structure

```
WeekendRecommendations
├── Books (BookTok Trending) - unchanged
├── Movies (Streaming Picks) - enhanced
├── Events (Local Events) - unchanged  
└── Entertainment Hub (NEW) - replaces Cultural Pulse
    ├── Top Movies
    ├── Must-Watch Series
    └── Theater & Plays
```

## Components and Interfaces

### 1. Enhanced Data Model

**Current Cultural Insights Structure**:
```typescript
cultural_insights?: {
  BookTok_trends?: string;
  streaming_releases?: string;
  social_media_phenomena?: string;
}
```

**New Entertainment Structure**:
```typescript
entertainment_recommendations?: {
  top_movies?: TopMovie[];
  must_watch_series?: TVSeries[];
  theater_plays?: TheaterPlay[];
}

interface TopMovie {
  title: string;
  genre: string;
  rating: string; // e.g., "8.5/10", "95% RT"
  platform: string; // Netflix, Prime Video, etc.
  description: string;
  release_year?: number;
  runtime?: string; // e.g., "2h 15m"
}

interface TVSeries {
  title: string;
  genre: string;
  rating: string;
  platform: string;
  description: string;
  seasons: number;
  episodes_per_season?: number;
  status: 'ongoing' | 'completed' | 'new_season';
}

interface TheaterPlay {
  title: string;
  genre: string;
  venue?: string;
  city?: string;
  description: string;
  show_times?: string;
  ticket_info?: string;
  rating?: string;
}
```

### 2. Component Structure Replacement

**Remove Cultural Pulse Section**:
```tsx
// REMOVE THIS SECTION
{weekendData.cultural_insights && (
  <div className="cultural-insights">
    <h4>🔥 Cultural Pulse</h4>
    // ... existing cultural insights content
  </div>
)}
```

**Add Entertainment Hub Section**:
```tsx
// ADD THIS SECTION
{weekendData.entertainment_recommendations && (
  <div className="entertainment-hub">
    <h4>🎬 Entertainment Hub</h4>
    <div className="entertainment-categories">
      {/* Top Movies */}
      {weekendData.entertainment_recommendations.top_movies && (
        <div className="entertainment-category">
          <h5>🍿 Top Movies</h5>
          <div className="entertainment-grid">
            {weekendData.entertainment_recommendations.top_movies.map((movie, index) => (
              <MovieCard key={index} movie={movie} />
            ))}
          </div>
        </div>
      )}
      
      {/* Must-Watch Series */}
      {weekendData.entertainment_recommendations.must_watch_series && (
        <div className="entertainment-category">
          <h5>📺 Must-Watch Series</h5>
          <div className="entertainment-grid">
            {weekendData.entertainment_recommendations.must_watch_series.map((series, index) => (
              <SeriesCard key={index} series={series} />
            ))}
          </div>
        </div>
      )}
      
      {/* Theater & Plays */}
      {weekendData.entertainment_recommendations.theater_plays && (
        <div className="entertainment-category">
          <h5>🎭 Theater & Plays</h5>
          <div className="entertainment-grid">
            {weekendData.entertainment_recommendations.theater_plays.map((play, index) => (
              <PlayCard key={index} play={play} />
            ))}
          </div>
        </div>
      )}
    </div>
  </div>
)}
```

### 3. Individual Card Components

**Movie Card Design**:
```tsx
const MovieCard: React.FC<{movie: TopMovie}> = ({ movie }) => (
  <div className="entertainment-card movie-card">
    <div className="card-header">
      <div className="platform-badge">{movie.platform}</div>
      <div className="rating-badge">{movie.rating}</div>
    </div>
    <h6 className="entertainment-title">{movie.title}</h6>
    <div className="entertainment-meta">
      <span className="genre">{movie.genre}</span>
      {movie.runtime && <span className="runtime">{movie.runtime}</span>}
      {movie.release_year && <span className="year">{movie.release_year}</span>}
    </div>
    <p className="entertainment-description">{movie.description}</p>
  </div>
);
```

**Series Card Design**:
```tsx
const SeriesCard: React.FC<{series: TVSeries}> = ({ series }) => (
  <div className="entertainment-card series-card">
    <div className="card-header">
      <div className="platform-badge">{series.platform}</div>
      <div className="rating-badge">{series.rating}</div>
    </div>
    <h6 className="entertainment-title">{series.title}</h6>
    <div className="entertainment-meta">
      <span className="genre">{series.genre}</span>
      <span className="seasons">{series.seasons} Season{series.seasons > 1 ? 's' : ''}</span>
      <span className="status-badge status-{series.status}">{series.status.replace('_', ' ')}</span>
    </div>
    <p className="entertainment-description">{series.description}</p>
  </div>
);
```

**Play Card Design**:
```tsx
const PlayCard: React.FC<{play: TheaterPlay}> = ({ play }) => (
  <div className="entertainment-card play-card">
    <div className="card-header">
      {play.rating && <div className="rating-badge">{play.rating}</div>}
    </div>
    <h6 className="entertainment-title">{play.title}</h6>
    <div className="entertainment-meta">
      <span className="genre">{play.genre}</span>
      {play.venue && <span className="venue">📍 {play.venue}</span>}
      {play.city && <span className="city">{play.city}</span>}
    </div>
    <p className="entertainment-description">{play.description}</p>
    {play.show_times && (
      <div className="show-info">
        <span className="show-times">🕐 {play.show_times}</span>
      </div>
    )}
    {play.ticket_info && (
      <div className="ticket-info">
        <span className="tickets">🎫 {play.ticket_info}</span>
      </div>
    )}
  </div>
);
```

## CSS Design System

### 1. Entertainment Hub Styling

```css
.entertainment-hub {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.entertainment-hub h4 {
  margin: 0 0 1.5rem 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.entertainment-categories {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.entertainment-category {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.entertainment-category h5 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
}

.entertainment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}
```

### 2. Entertainment Card Styling

```css
.entertainment-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.entertainment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.platform-badge,
.rating-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.rating-badge {
  background: rgba(76, 175, 80, 0.3);
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.entertainment-title {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  line-height: 1.3;
  color: white;
}

.entertainment-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.entertainment-meta span {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
  opacity: 0.9;
}

.status-badge {
  text-transform: capitalize;
}

.status-ongoing {
  background: rgba(76, 175, 80, 0.2) !important;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.status-new_season {
  background: rgba(255, 193, 7, 0.2) !important;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.entertainment-description {
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0 0 0.75rem 0;
  opacity: 0.9;
}

.show-info,
.ticket-info {
  margin-top: 0.5rem;
}

.show-info span,
.ticket-info span {
  font-size: 0.8rem;
  opacity: 0.8;
  display: block;
  margin-bottom: 0.25rem;
}
```

## Data Flow Changes

### 1. Backend Integration

The Weekend Events Agent will need to generate entertainment recommendations instead of cultural insights:

```python
# In content_generator.py or weekend events agent
def generate_entertainment_recommendations():
    return {
        "top_movies": [
            {
                "title": "Dune: Part Two",
                "genre": "Sci-Fi Epic",
                "rating": "8.8/10",
                "platform": "Max",
                "description": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
                "release_year": 2024,
                "runtime": "2h 46m"
            }
        ],
        "must_watch_series": [
            {
                "title": "The Bear",
                "genre": "Comedy-Drama",
                "rating": "9.1/10",
                "platform": "Hulu",
                "description": "A young chef from the fine dining world returns to Chicago to run his deceased brother's sandwich shop.",
                "seasons": 3,
                "status": "ongoing"
            }
        ],
        "theater_plays": [
            {
                "title": "Hamilton",
                "genre": "Musical",
                "venue": "Richard Rodgers Theatre",
                "city": "New York",
                "description": "The story of American founding father Alexander Hamilton.",
                "show_times": "Tue-Sun 8PM, Wed & Sat 2PM",
                "ticket_info": "From $79"
            }
        ]
    }
```

### 2. Component Props Update

Update the WeekendData interface:

```typescript
interface WeekendData {
  books?: Book[];
  movies?: Movie[];
  events?: Event[];
  entertainment_recommendations?: {
    top_movies?: TopMovie[];
    must_watch_series?: TVSeries[];
    theater_plays?: TheaterPlay[];
  };
  description?: string;
}
```

## Error Handling

### Fallback Mechanisms
1. **No Entertainment Data**: Show existing movies section if available
2. **Partial Data**: Display available categories, hide empty ones
3. **Invalid Data**: Sanitize and show with default values

### Graceful Degradation
- If entertainment_recommendations is missing, component continues to work
- Individual categories can be missing without breaking the layout
- Maintains backward compatibility with existing cultural_insights data

## Testing Strategy

### Unit Tests
- Component rendering with entertainment data
- Fallback behavior when data is missing
- Card component rendering with various data combinations

### Integration Tests
- Full weekend recommendations with entertainment section
- Backend data generation and frontend display
- Responsive design across different screen sizes

### User Experience Tests
- Visual consistency with existing design
- Information clarity and readability
- Interactive elements and hover states

## Migration Strategy

1. **Phase 1**: Add new entertainment data structure alongside existing cultural insights
2. **Phase 2**: Update frontend to display entertainment section
3. **Phase 3**: Update backend to generate entertainment data
4. **Phase 4**: Remove cultural insights code after verification

## Performance Considerations

- Maintain existing component performance
- Efficient rendering of entertainment cards
- Proper image lazy loading if entertainment images are added later
- Minimal bundle size impact

## Accessibility

- Maintain semantic HTML structure
- Ensure proper heading hierarchy (h4 → h5 → h6)
- Preserve keyboard navigation
- Keep color contrast ratios for readability

## Success Metrics

- **User Engagement**: Increased interaction with weekend recommendations
- **Content Relevance**: More actionable entertainment suggestions
- **Visual Consistency**: Seamless integration with existing design
- **Performance**: No degradation in component load times