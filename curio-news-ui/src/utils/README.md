# Core Data Transformation Layer

This directory contains the core utilities for transforming Bedrock agent outputs into the mobile card UI format.

## Overview

The data transformation layer consists of three main modules:

1. **Script Segmentation** (`scriptSegmentation.ts`) - Splits long scripts into 15-30 second segments
2. **Category Mapping** (`categoryMapping.ts`) - Maps news categories to visual styles and icons
3. **Card Transformation** (`cardTransformer.ts`) - Transforms agent outputs into StoryCard format

## Script Segmentation

### Key Functions

- `segmentScript()` - Main segmentation algorithm using word timings
- `fallbackSegmentation()` - Fallback when word timings unavailable
- `calculateTotalDuration()` - Calculate total script duration
- `validateSegments()` - Validate segment quality

### Features

- Intelligent sentence boundary detection
- Natural breaks at punctuation marks
- Configurable duration targets (15-30 seconds)
- Fallback to word-count estimation

### Example

```typescript
import { segmentScript } from './utils';

const segments = segmentScript(script, wordTimings, 25);
// Returns: [
//   { text: "...", duration: 23.5, startTime: 0, endTime: 23.5 },
//   { text: "...", duration: 27.2, startTime: 23.5, endTime: 50.7 }
// ]
```

## Category Mapping

### Supported Categories

- `favorite` - Featured/highlighted stories (pink-rose gradient, Heart icon)
- `world` - International news (blue-indigo gradient, Globe icon)
- `local` - Local/regional news (green-emerald gradient, MapPin icon)
- `event` - Events/happenings (purple-violet gradient, Calendar icon)
- `movie` - Film/cinema (red-orange gradient, Film icon)
- `music` - Music/concerts (cyan-blue gradient, Music icon)
- `book` - Books/literature (amber-yellow gradient, Book icon)

### Key Functions

- `mapNewsCategory()` - Map API category strings to CategoryType
- `inferCategory()` - Infer category from title/summary content
- `getCategoryEmoji()` - Get emoji for category
- `getCategoryColor()` - Get hex color for category
- `getCategoryKeywords()` - Get Unsplash search keywords

### Example

```typescript
import { mapNewsCategory, getCategoryEmoji } from './utils';

const category = mapNewsCategory('international'); // Returns: 'world'
const emoji = getCategoryEmoji('world'); // Returns: '🌍'
```

## Card Transformation

### Main Function

`transformToCards(bootstrapData)` - Converts bootstrap API response into StoryCard array

### Process Flow

1. Create overview card (first card)
2. Segment the script using word timings
3. Create favorite story card (if available)
4. Create story cards from curated news
5. Create entertainment cards (if available)

### Card Types Generated

- **Overview Card** - Summary of today's stories
- **Favorite Card** - Story Selector's top pick
- **Story Cards** - Individual news items
- **Entertainment Cards** - Weekend recommendations

### Example

```typescript
import { transformToCards } from './utils';

const cards = transformToCards(bootstrapData);
// Returns: [
//   { id: 0, type: 'overview', title: 'Today in Curio 🪄', ... },
//   { id: 1, type: 'favorite', title: 'Top Story', ... },
//   { id: 2, type: 'world', title: 'News Item 1', ... },
//   ...
// ]
```

### Media Handling

The transformer implements a three-tier fallback strategy:

1. **Primary**: Media Enhancer agent output (videos/images/GIFs)
2. **Secondary**: Unsplash API with category keywords
3. **Tertiary**: Placeholder with category emoji

## Testing

Comprehensive test suite in `__tests__/dataTransformation.test.ts`:

```bash
npm test -- --watchAll=false --testPathPattern=dataTransformation
```

### Test Coverage

- ✅ Script segmentation with word timings
- ✅ Fallback segmentation without timings
- ✅ Duration calculation
- ✅ Segment validation
- ✅ Category mapping
- ✅ Category inference
- ✅ Card transformation
- ✅ Graceful handling of missing data

## Integration

Import utilities from the index file:

```typescript
import {
  transformToCards,
  segmentScript,
  mapNewsCategory,
  getCategoryEmoji
} from './utils';
```

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:

- **Requirement 10.1, 10.2, 10.3**: Script segmentation into 15-30 second segments
- **Requirement 9.1, 9.2, 9.3, 9.5, 9.6**: Agent output transformation
- **Requirement 3.1, 3.2, 3.3**: Category mapping and visual configuration

## Next Steps

The data transformation layer is complete and ready for integration with:

1. BackgroundMedia component (Task 3)
2. CategoryTag component (Task 4)
3. StoryCard component (Task 6)
4. CurioCardStack container (Task 7)
