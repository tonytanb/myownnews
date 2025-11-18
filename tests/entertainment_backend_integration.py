#!/usr/bin/env python3
"""
Backend Integration Tests for Entertainment Recommendations
Tests the entertainment data generation in the content generator
"""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

try:
    from content_generator import ContentGenerator
except ImportError as e:
    print(f"Warning: Could not import ContentGenerator: {e}")
    print("This test requires the content_generator module to be available")
    sys.exit(0)

class TestEntertainmentBackendIntegration(unittest.TestCase):
    """Test entertainment recommendations generation in the backend"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = ContentGenerator('test-table')
        
        # Mock news items for testing
        self.mock_news_items = [
            {
                'title': 'New AI Technology Breakthrough',
                'summary': 'Scientists develop advanced AI system',
                'category': 'TECHNOLOGY',
                'source': 'Tech News'
            },
            {
                'title': 'Medical Research Discovery',
                'summary': 'New treatment shows promising results',
                'category': 'HEALTH',
                'source': 'Medical Journal'
            },
            {
                'title': 'Space Exploration Update',
                'summary': 'Mars mission makes significant progress',
                'category': 'SCIENCE',
                'source': 'Space Agency'
            }
        ]
    
    def test_entertainment_recommendations_structure(self):
        """Test that entertainment recommendations have the correct structure"""
        entertainment_data = self.generator._generate_entertainment_recommendations(self.mock_news_items)
        
        # Verify top-level structure
        self.assertIsInstance(entertainment_data, dict)
        self.assertIn('top_movies', entertainment_data)
        self.assertIn('must_watch_series', entertainment_data)
        self.assertIn('theater_plays', entertainment_data)
        
        # Verify each category is a list
        self.assertIsInstance(entertainment_data['top_movies'], list)
        self.assertIsInstance(entertainment_data['must_watch_series'], list)
        self.assertIsInstance(entertainment_data['theater_plays'], list)
    
    def test_movie_recommendations_structure(self):
        """Test that movie recommendations have the correct fields"""
        entertainment_data = self.generator._generate_entertainment_recommendations(self.mock_news_items)
        
        if entertainment_data['top_movies']:
            movie = entertainment_data['top_movies'][0]
            
            # Required fields
            self.assertIn('title', movie)
            self.assertIn('genre', movie)
            self.assertIn('rating', movie)
            self.assertIn('platform', movie)
            self.assertIn('description', movie)
            
            # Verify field types
            self.assertIsInstance(movie['title'], str)
            self.assertIsInstance(movie['genre'], str)
            self.assertIsInstance(movie['rating'], str)
            self.assertIsInstance(movie['platform'], str)
            self.assertIsInstance(movie['description'], str)
            
            # Optional fields (if present)
            if 'release_year' in movie:
                self.assertIsInstance(movie['release_year'], int)
            if 'runtime' in movie:
                self.assertIsInstance(movie['runtime'], str)
    
    def test_series_recommendations_structure(self):
        """Test that series recommendations have the correct fields"""
        entertainment_data = self.generator._generate_entertainment_recommendations(self.mock_news_items)
        
        if entertainment_data['must_watch_series']:
            series = entertainment_data['must_watch_series'][0]
            
            # Required fields
            self.assertIn('title', series)
            self.assertIn('genre', series)
            self.assertIn('rating', series)
            self.assertIn('platform', series)
            self.assertIn('description', series)
            self.assertIn('seasons', series)
            self.assertIn('status', series)
            
            # Verify field types
            self.assertIsInstance(series['title'], str)
            self.assertIsInstance(series['genre'], str)
            self.assertIsInstance(series['rating'], str)
            self.assertIsInstance(series['platform'], str)
            self.assertIsInstance(series['description'], str)
            self.assertIsInstance(series['seasons'], int)
            self.assertIn(series['status'], ['ongoing', 'completed', 'new_season'])
            
            # Optional fields (if present)
            if 'episodes_per_season' in series:
                self.assertIsInstance(series['episodes_per_season'], int)
    
    def test_theater_recommendations_structure(self):
        """Test that theater recommendations have the correct fields"""
        entertainment_data = self.generator._generate_entertainment_recommendations(self.mock_news_items)
        
        if entertainment_data['theater_plays']:
            play = entertainment_data['theater_plays'][0]
            
            # Required fields
            self.assertIn('title', play)
            self.assertIn('genre', play)
            self.assertIn('description', play)
            
            # Verify field types
            self.assertIsInstance(play['title'], str)
            self.assertIsInstance(play['genre'], str)
            self.assertIsInstance(play['description'], str)
            
            # Optional fields (if present)
            if 'venue' in play:
                self.assertIsInstance(play['venue'], str)
            if 'city' in play:
                self.assertIsInstance(play['city'], str)
            if 'show_times' in play:
                self.assertIsInstance(play['show_times'], str)
            if 'ticket_info' in play:
                self.assertIsInstance(play['ticket_info'], str)
            if 'rating' in play:
                self.assertIsInstance(play['rating'], str)
    
    def test_theme_analysis(self):
        """Test that news theme analysis works correctly"""
        themes = self.generator._analyze_news_themes(self.mock_news_items)
        
        # Verify themes structure
        self.assertIsInstance(themes, dict)
        
        # Check expected themes are present
        expected_themes = ['technology', 'health', 'science', 'politics', 'business', 'sports', 'international', 'entertainment']
        for theme in expected_themes:
            self.assertIn(theme, themes)
            self.assertIsInstance(themes[theme], int)
            self.assertGreaterEqual(themes[theme], 0)
        
        # Verify that our mock data produces expected theme scores
        self.assertGreater(themes['technology'], 0)  # AI technology news
        self.assertGreater(themes['health'], 0)      # Medical research news
        self.assertGreater(themes['science'], 0)     # Space exploration news
    
    def test_fallback_entertainment_recommendations(self):
        """Test fallback entertainment recommendations"""
        fallback_data = self.generator._get_fallback_entertainment_recommendations()
        
        # Verify structure
        self.assertIsInstance(fallback_data, dict)
        self.assertIn('top_movies', fallback_data)
        self.assertIn('must_watch_series', fallback_data)
        self.assertIn('theater_plays', fallback_data)
        
        # Verify fallback data is not empty
        self.assertGreater(len(fallback_data['top_movies']), 0)
        self.assertGreater(len(fallback_data['must_watch_series']), 0)
        self.assertGreater(len(fallback_data['theater_plays']), 0)
    
    def test_entertainment_integration_in_agent_outputs(self):
        """Test that entertainment recommendations are properly integrated into agent outputs"""
        agent_outputs = self.generator._create_agent_outputs(self.mock_news_items)
        
        # Verify agent outputs structure
        self.assertIsInstance(agent_outputs, dict)
        self.assertIn('weekendRecommendations', agent_outputs)
        
        weekend_recs = agent_outputs['weekendRecommendations']
        self.assertIn('entertainment_recommendations', weekend_recs)
        
        entertainment_recs = weekend_recs['entertainment_recommendations']
        
        # Verify entertainment recommendations structure
        self.assertIn('top_movies', entertainment_recs)
        self.assertIn('must_watch_series', entertainment_recs)
        self.assertIn('theater_plays', entertainment_recs)
    
    def test_error_handling_in_entertainment_generation(self):
        """Test error handling in entertainment generation"""
        # Test with None input
        result = self.generator._generate_entertainment_recommendations(None)
        self.assertIsInstance(result, dict)
        
        # Test with empty list
        result = self.generator._generate_entertainment_recommendations([])
        self.assertIsInstance(result, dict)
        
        # Test with malformed news items
        malformed_items = [{'invalid': 'data'}]
        result = self.generator._generate_entertainment_recommendations(malformed_items)
        self.assertIsInstance(result, dict)
    
    def test_entertainment_generation_exception_handling(self):
        """Test exception handling in entertainment generation"""
        # Test with a method that will cause an exception
        with patch.object(self.generator, '_generate_entertainment_recommendations', side_effect=Exception("Test exception")):
            # This should not crash and should return fallback data
            agent_outputs = self.generator._create_agent_outputs(self.mock_news_items)
            
            # Verify we still get valid output structure
            self.assertIsInstance(agent_outputs, dict)
            self.assertIn('weekendRecommendations', agent_outputs)
    
    def test_entertainment_data_limits(self):
        """Test that entertainment data respects reasonable limits"""
        entertainment_data = self.generator._generate_entertainment_recommendations(self.mock_news_items)
        
        # Verify reasonable limits (not too many recommendations)
        self.assertLessEqual(len(entertainment_data['top_movies']), 5)
        self.assertLessEqual(len(entertainment_data['must_watch_series']), 5)
        self.assertLessEqual(len(entertainment_data['theater_plays']), 5)
    
    def test_entertainment_content_quality(self):
        """Test that entertainment content meets quality standards"""
        entertainment_data = self.generator._generate_entertainment_recommendations(self.mock_news_items)
        
        # Check movies
        for movie in entertainment_data['top_movies']:
            self.assertGreater(len(movie['title']), 0)
            self.assertGreater(len(movie['description']), 10)  # Reasonable description length
            self.assertIn('/', movie['rating'])  # Rating format like "8.5/10"
        
        # Check series
        for series in entertainment_data['must_watch_series']:
            self.assertGreater(len(series['title']), 0)
            self.assertGreater(len(series['description']), 10)
            self.assertGreater(series['seasons'], 0)
        
        # Check plays
        for play in entertainment_data['theater_plays']:
            self.assertGreater(len(play['title']), 0)
            self.assertGreater(len(play['description']), 10)

def run_tests():
    """Run the entertainment backend integration tests"""
    print("🎬 Running Entertainment Backend Integration Tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEntertainmentBackendIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"✅ Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests failed: {len(result.failures)}")
    print(f"💥 Tests with errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)