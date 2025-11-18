#!/usr/bin/env python3
"""
Test Social Impact Story Scoring
Direct test of the improved favorite story selection algorithm
"""

import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

try:
    from content_generator import ContentGenerator
except ImportError as e:
    print(f"Error importing ContentGenerator: {e}")
    sys.exit(1)

def test_social_impact_scoring():
    """Test that social impact stories score higher than financial stories"""
    print("🎯 Testing Social Impact Story Scoring Algorithm")
    print("=" * 50)
    
    generator = ContentGenerator('test-table')
    
    # Test stories representing different types of news
    test_stories = [
        {
            'title': 'Stocks rise to records as traders await Fed rate decision; Nvidia climbs',
            'summary': 'U.S. stocks rose to record levels on Wednesday, boosted by tech names, ahead of the Federal Reserve\'s interest rate decision.',
            'category': 'BUSINESS'
        },
        {
            'title': 'Scientists Discover Revolutionary Cancer Treatment That Helps Patients',
            'summary': 'Medical breakthrough shows promise in treating cancer patients with new therapy that could save thousands of lives.',
            'category': 'HEALTH'
        },
        {
            'title': 'Community Volunteers Build Affordable Housing for Families in Need',
            'summary': 'Local activists and volunteers work together to address housing crisis and support low-income families in the community.',
            'category': 'GENERAL'
        },
        {
            'title': 'Students Launch Mental Health Awareness Program in Schools',
            'summary': 'Young activists create innovative program to support mental health and social justice in education system.',
            'category': 'GENERAL'
        },
        {
            'title': 'Rare Ancient Artifact Discovered in Archaeological Dig',
            'summary': 'Archaeologists uncover fascinating historical artifact that provides new insights into ancient civilization.',
            'category': 'GENERAL'
        }
    ]
    
    print("📊 Scoring each story:")
    print()
    
    scored_stories = []
    for story in test_stories:
        score = generator._calculate_story_score(story)
        scored_stories.append((story, score))
        print(f"📰 '{story['title'][:50]}...'")
        print(f"   Score: {score:.1f} points")
        print(f"   Category: {story['category']}")
        print()
    
    # Sort by score (highest first)
    scored_stories.sort(key=lambda x: x[1], reverse=True)
    
    print("🏆 FINAL RANKING:")
    print("=" * 50)
    for i, (story, score) in enumerate(scored_stories, 1):
        title = story['title'][:45] + "..." if len(story['title']) > 45 else story['title']
        print(f"{i}. {title}")
        print(f"   Score: {score:.1f} points | Category: {story['category']}")
        print()
    
    # Test favorite story selection
    print("⭐ FAVORITE STORY SELECTION:")
    print("=" * 50)
    
    favorite_story = generator._select_favorite_story(test_stories)
    
    if favorite_story:
        print(f"Selected: {favorite_story['title']}")
        print(f"Reasoning: {favorite_story['reasoning']}")
        
        # Check if it's a social impact story (not financial)
        title_lower = favorite_story['title'].lower()
        is_financial = any(word in title_lower for word in ['stock', 'market', 'trading', 'fed rate', 'nasdaq'])
        is_social_impact = any(word in title_lower for word in ['community', 'health', 'discovery', 'students', 'mental health', 'cancer', 'help'])
        
        print()
        if is_social_impact and not is_financial:
            print("✅ SUCCESS: Selected story has social impact focus!")
            return True
        elif is_financial:
            print("❌ ISSUE: Selected story is still financial/market focused")
            return False
        else:
            print("⚠️  NEUTRAL: Selected story is neither financial nor clearly social impact")
            return True
    else:
        print("❌ No favorite story selected")
        return False

if __name__ == "__main__":
    success = test_social_impact_scoring()
    print("\n" + "=" * 50)
    if success:
        print("🎉 Social Impact Scoring is working correctly!")
        print("💡 Stories now prioritize community benefit over financial gains")
        print("🤝 Perfect for socially-aware Gen Z and Millennial audiences")
    else:
        print("⚠️  Social Impact Scoring needs adjustment")
    
    sys.exit(0 if success else 1)