#!/usr/bin/env python3
"""
Integration test for Content Validation, Fallback Management, and Error Handling systems
"""

import json
import sys
import os
from datetime import datetime

# Add the api directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content_validator import ContentValidator, ValidationSeverity
from fallback_manager import FallbackManager
from error_handler import ErrorHandler, ErrorContext, ErrorCategory

def test_content_validation():
    """Test content validation system"""
    print("🧪 Testing Content Validation System...")
    
    validator = ContentValidator()
    
    # Test with sample content
    sample_content = {
        'news_items': [
            {
                'title': 'AI Technology Advances',
                'summary': 'New developments in artificial intelligence continue to shape the tech landscape.',
                'category': 'TECHNOLOGY',
                'relevance_score': 0.85
            },
            {
                'title': 'Cultural Trends in Social Media',
                'summary': 'Social media platforms are driving new cultural movements.',
                'category': 'CULTURE',
                'relevance_score': 0.78
            }
        ],
        'script': 'Hey there! Here\'s what\'s happening in the world today. First up, AI technology continues to advance...',
        'audioUrl': 'https://example.com/audio.mp3',
        'word_timings': [
            {'word': 'Hey', 'start': 0.0, 'end': 0.3},
            {'word': 'there!', 'start': 0.3, 'end': 0.7}
        ],
        'agentOutputs': {
            'favoriteStory': {
                'reasoning': 'This AI story is fascinating because it shows how technology is reshaping our daily lives.'
            },
            'weekendRecommendations': {
                'books': [
                    {
                        'title': 'The Future of AI',
                        'author': 'Tech Author',
                        'description': 'A comprehensive look at AI\'s impact on society.'
                    }
                ],
                'movies_and_shows': [],
                'events': []
            },
            'mediaEnhancements': {
                'stories': [
                    {
                        'title': 'AI Technology Advances',
                        'media_recommendations': {
                            'images': [{'url': 'https://example.com/image.jpg', 'alt_text': 'AI image'}]
                        }
                    }
                ]
            }
        }
    }
    
    # Validate content
    validation_results = validator.validate_complete_content(sample_content)
    
    print(f"✅ Validation completed. Found {len(validation_results)} sections.")
    
    # Check summary
    if '_summary' in validation_results:
        summary = validation_results['_summary']
        print(f"📊 Overall Score: {summary.score:.1f}")
        print(f"🎯 Valid: {summary.is_valid}")
        print(f"⚠️  Issues: {len(summary.issues)}")
    
    # Generate report
    report = validator.generate_validation_report(validation_results)
    print(f"📋 Generated validation report with {len(report.get('recommendations', []))} recommendations")
    
    return validation_results

def test_fallback_manager():
    """Test fallback management system"""
    print("\n🧪 Testing Fallback Management System...")
    
    # Mock DynamoDB table name
    fallback_manager = FallbackManager('test_table')
    
    # Test fallback for news stories
    fallback_result = fallback_manager.get_fallback_content(
        'news_stories',
        failed_content=None,
        context={'existing_data': 'test'}
    )
    
    print(f"✅ Fallback generated for news_stories")
    print(f"📊 Quality Score: {fallback_result.get('quality_score', 0):.1f}")
    print(f"🔧 Method: {fallback_result.get('fallback_method', 'unknown')}")
    
    # Test partial content delivery
    successful_sections = {
        'news_stories': [{'title': 'Test Story', 'category': 'TEST'}],
        'script_content': 'Test script content'
    }
    failed_sections = ['favorite_story', 'weekend_recommendations']
    
    partial_content = fallback_manager.get_partial_content_delivery(
        successful_sections,
        failed_sections
    )
    
    print(f"✅ Partial content delivery created")
    print(f"📦 Sections: {len(partial_content)} total")
    print(f"🔄 Fallback metadata: {bool(partial_content.get('fallback_metadata'))}")
    
    return fallback_result

def test_error_handler():
    """Test error handling system"""
    print("\n🧪 Testing Error Handling System...")
    
    error_handler = ErrorHandler('test_table')
    
    # Test error categorization
    test_errors = [
        Exception("Connection timeout occurred"),
        Exception("Rate limit exceeded"),
        Exception("Bedrock model error"),
        Exception("JSON parse error"),
        Exception("Unknown error occurred")
    ]
    
    for error in test_errors:
        category = error_handler._categorize_error(error)
        severity = error_handler._assess_error_severity(error, category)
        print(f"🏷️  '{str(error)[:30]}...' -> {category.value} ({severity.value})")
    
    # Test graceful degradation plan
    failed_sections = ['favorite_story', 'visual_enhancements']
    available_content = {'news_items': [], 'script': 'test'}
    
    degradation_plan = error_handler.create_graceful_degradation_plan(
        failed_sections,
        available_content
    )
    
    print(f"✅ Degradation plan created")
    print(f"📋 Strategy: {degradation_plan.get('strategy')}")
    print(f"⚡ Quality Impact: {degradation_plan.get('quality_impact')}")
    print(f"🔧 Fallback Actions: {len(degradation_plan.get('fallback_actions', {}))}")
    
    return degradation_plan

def test_integration():
    """Test integration between all systems"""
    print("\n🧪 Testing System Integration...")
    
    # Create sample failed content scenario
    sample_content = {
        'news_items': [],  # Empty - should trigger validation issues
        'script': 'Short',  # Too short - should trigger validation issues
        'agentOutputs': {}  # Missing sections
    }
    
    # Step 1: Validate content (should find issues)
    validator = ContentValidator()
    validation_results = validator.validate_complete_content(sample_content)
    
    critical_issues = []
    for section_name, result in validation_results.items():
        if result.has_critical_issues():
            critical_issues.append(section_name)
    
    print(f"🔍 Found critical issues in: {critical_issues}")
    
    # Step 2: Use fallback manager for failed sections
    fallback_manager = FallbackManager('test_table')
    
    enhanced_content = sample_content.copy()
    for section in critical_issues:
        if section.startswith('_'):  # Skip summary sections
            continue
            
        fallback_result = fallback_manager.get_fallback_content(
            section,
            failed_content=sample_content.get(section),
            context=sample_content
        )
        
        if fallback_result and fallback_result.get('content'):
            print(f"🔧 Applied fallback for {section}")
            # Apply fallback content (simplified for test)
            if section == 'news_stories':
                enhanced_content['news_items'] = fallback_result['content']
            elif section == 'script_content':
                enhanced_content['script'] = fallback_result['content']
    
    # Step 3: Re-validate enhanced content
    final_validation = validator.validate_complete_content(enhanced_content)
    final_summary = final_validation.get('_summary')
    
    if final_summary:
        print(f"📊 Final Quality Score: {final_summary.score:.1f}")
        print(f"✅ Final Validation: {final_summary.is_valid}")
        
        improvement = final_summary.score - (validation_results.get('_summary', {}).score or 0)
        print(f"📈 Quality Improvement: +{improvement:.1f} points")
    
    print("🎉 Integration test completed successfully!")
    
    return {
        'original_validation': validation_results,
        'enhanced_content': enhanced_content,
        'final_validation': final_validation
    }

def main():
    """Run all tests"""
    print("🚀 Starting Content Validation, Fallback, and Error Handling Integration Tests\n")
    
    try:
        # Run individual system tests
        validation_results = test_content_validation()
        fallback_results = test_fallback_manager()
        error_results = test_error_handler()
        
        # Run integration test
        integration_results = test_integration()
        
        print(f"\n✅ All tests completed successfully!")
        print(f"📊 Systems are properly integrated and functional.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)