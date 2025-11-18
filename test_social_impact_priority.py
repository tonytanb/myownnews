#!/usr/bin/env python3
"""
Test to verify that social impact stories are prioritized over financial news
"""

import requests
import json
from datetime import datetime

API_URL = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod"

def test_social_impact_prioritization():
    """Test that favorite story selection prioritizes social impact"""
    print("🤝 TESTING SOCIAL IMPACT STORY PRIORITIZATION")
    print("=" * 60)
    
    try:
        # Test with bootstrap endpoint
        print(f"\n📡 Calling API: {API_URL}/bootstrap")
        response = requests.get(f"{API_URL}/bootstrap", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            agent_outputs = data.get('agentOutputs', {})
            favorite_story = agent_outputs.get('favoriteStory', {})
            news_items = data.get('news_items', [])
            
            print(f"\n📊 Content Analysis:")
            print(f"   - Total news items: {len(news_items)}")
            print(f"   - Has favorite story: {bool(favorite_story)}")
            
            if favorite_story:
                title = favorite_story.get('title', '').lower()
                reasoning = favorite_story.get('reasoning', '').lower()
                category = favorite_story.get('category', '')
                
                print(f"\n⭐ SELECTED FAVORITE STORY:")
                print(f"   📰 Title: {favorite_story.get('title', '')}")
                print(f"   🏷️  Category: {category}")
                print(f"   🧠 Reasoning: {reasoning}")
                
                # Check for social impact indicators
                social_impact_keywords = [
                    'community', 'society', 'social', 'help', 'support',
                    'education', 'health', 'accessibility', 'equality',
                    'diversity', 'inclusion', 'awareness', 'program',
                    'initiative', 'outreach', 'service', 'aid'
                ]
                
                financial_keywords = [
                    'stock', 'market', 'trading', 'investor', 'wall street',
                    'nasdaq', 'dow jones', 'earnings', 'shares', 'dividend'
                ]
                
                social_matches = sum(1 for keyword in social_impact_keywords if keyword in title or keyword in reasoning)
                financial_matches = sum(1 for keyword in financial_keywords if keyword in title or keyword in reasoning)
                
                print(f"\n📈 Keyword Analysis:")
                print(f"   🤝 Social impact keywords found: {social_matches}")
                print(f"   💰 Financial keywords found: {financial_matches}")
                
                # Analyze all news items
                print(f"\n📋 ALL NEWS ITEMS:")
                for i, item in enumerate(news_items, 1):
                    item_title = item.get('title', '').lower()
                    item_category = item.get('category', '')
                    
                    item_social = sum(1 for keyword in social_impact_keywords if keyword in item_title)
                    item_financial = sum(1 for keyword in financial_keywords if keyword in item_title)
                    
                    is_selected = item.get('title', '') == favorite_story.get('title', '')
                    marker = "⭐ SELECTED" if is_selected else ""
                    
                    print(f"\n   {i}. {marker}")
                    print(f"      Title: {item.get('title', '')[:70]}...")
                    print(f"      Category: {item_category}")
                    print(f"      Social keywords: {item_social} | Financial keywords: {item_financial}")
                
                # Determine if selection is good
                print(f"\n✅ EVALUATION:")
                if social_matches > 0 and financial_matches == 0:
                    print(f"   ✅ EXCELLENT: Selected story has strong social impact focus!")
                    print(f"   🎯 The algorithm correctly prioritized social benefit over financial news.")
                    return True
                elif social_matches > financial_matches:
                    print(f"   ✅ GOOD: Selected story leans toward social impact.")
                    print(f"   🎯 Social keywords ({social_matches}) > Financial keywords ({financial_matches})")
                    return True
                elif financial_matches > 0:
                    print(f"   ⚠️  WARNING: Selected story has financial focus.")
                    print(f"   💰 Financial keywords ({financial_matches}) detected.")
                    print(f"   🔧 Consider adjusting scoring weights to prioritize social impact more.")
                    return False
                else:
                    print(f"   ℹ️  NEUTRAL: Story is neither strongly social nor financial.")
                    return True
            else:
                print("   ❌ No favorite story found in response")
                return False
        else:
            print(f"   ❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"\n🚀 Starting Social Impact Prioritization Test")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    result = test_social_impact_prioritization()
    
    print(f"\n{'='*60}")
    if result:
        print("✅ TEST PASSED: Social impact prioritization is working!")
    else:
        print("⚠️  TEST NEEDS ATTENTION: Review favorite story selection")
    print(f"{'='*60}\n")
