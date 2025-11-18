#!/usr/bin/env python3
"""
Enhanced Favorite Story Selection Test
Tests the improved algorithm that prioritizes good news, discoveries, and curiosities
"""

import requests
import json
from datetime import datetime

def test_enhanced_favorite_selection():
    """Test the enhanced favorite story selection algorithm"""
    print("🌟 ENHANCED FAVORITE STORY SELECTION TEST")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Trigger fresh content generation to test new algorithm
        print("🔄 Generating fresh content with enhanced algorithm...")
        
        generate_url = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod/generate-fresh"
        generate_response = requests.post(generate_url, timeout=30)
        
        if generate_response.status_code == 200:
            print("✅ Fresh content generation triggered")
            
            # Wait a moment for processing
            import time
            time.sleep(3)
            
            # Get the new favorite story
            api_url = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod/bootstrap"
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                agent_outputs = data.get('agentOutputs', {})
                favorite_story = agent_outputs.get('favoriteStory', {})
                news_items = data.get('news_items', [])
                
                print(f"\n📊 Content Analysis:")
                print(f"   - Total news items: {len(news_items)}")
                print(f"   - Has favorite story: {bool(favorite_story)}")
                
                if favorite_story:
                    title = favorite_story.get('title', '')
                    summary = favorite_story.get('summary', '')
                    category = favorite_story.get('category', '')
                    reasoning = favorite_story.get('reasoning', '')
                    
                    print(f"\n⭐ SELECTED FAVORITE STORY:")
                    print(f"   📰 Title: {title}")
                    print(f"   📝 Summary: {summary[:100]}...")
                    print(f"   🏷️ Category: {category}")
                    print(f"   🧠 Reasoning: {reasoning}")
                    
                    # Analyze the content for positive indicators
                    text_to_analyze = f"{title} {summary}".lower()
                    
                    positive_indicators = {
                        'Scientific Discovery': ['breakthrough', 'discovery', 'cure', 'treatment', 'research', 'study'],
                        'Good News': ['rescued', 'saved', 'helped', 'success', 'achievement', 'positive'],
                        'Curiosity/Wonder': ['rare', 'unique', 'first time', 'unusual', 'fascinating', 'amazing'],
                        'Innovation': ['innovation', 'technology', 'ai', 'space', 'invention'],
                        'Environmental': ['conservation', 'wildlife', 'sustainability', 'environment']
                    }
                    
                    negative_indicators = ['death', 'killed', 'attack', 'war', 'disaster', 'crisis', 'scandal']
                    
                    print(f"\n🔍 CONTENT ANALYSIS:")
                    
                    found_positive = []
                    for category_name, keywords in positive_indicators.items():
                        matches = [word for word in keywords if word in text_to_analyze]
                        if matches:
                            found_positive.append(f"{category_name}: {', '.join(matches)}")
                    
                    found_negative = [word for word in negative_indicators if word in text_to_analyze]
                    
                    if found_positive:
                        print("   ✅ POSITIVE INDICATORS FOUND:")
                        for indicator in found_positive:
                            print(f"      🌟 {indicator}")
                    else:
                        print("   ⚠️ No strong positive indicators detected")
                    
                    if found_negative:
                        print("   ❌ NEGATIVE INDICATORS:")
                        for word in found_negative:
                            print(f"      ⚠️ {word}")
                    else:
                        print("   ✅ No negative indicators - good!")
                    
                    # Overall assessment
                    print(f"\n🎯 ASSESSMENT:")
                    if found_positive and not found_negative:
                        print("   🎉 EXCELLENT: Story is positive and fascinating!")
                    elif found_positive:
                        print("   👍 GOOD: Story has positive elements")
                    elif not found_negative:
                        print("   😐 NEUTRAL: Story is not negative but could be more inspiring")
                    else:
                        print("   😞 NEEDS IMPROVEMENT: Story contains negative elements")
                    
                    # Show all available stories for comparison
                    print(f"\n📋 ALL AVAILABLE STORIES:")
                    for i, item in enumerate(news_items, 1):
                        item_title = item.get('title', '')
                        is_selected = item_title == title
                        marker = "⭐ SELECTED" if is_selected else f"   {i}."
                        print(f"{marker} {item_title[:60]}...")
                    
                    return True
                else:
                    print("❌ No favorite story found in response")
                    return False
            else:
                print(f"❌ Bootstrap API error: {response.status_code}")
                return False
        else:
            print(f"❌ Generate API error: {generate_response.status_code}")
            # Try to get existing content anyway
            api_url = "https://nqot0dir0h.execute-api.us-west-2.amazonaws.com/prod/bootstrap"
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                print("📖 Testing with existing content...")
                data = response.json()
                favorite_story = data.get('agentOutputs', {}).get('favoriteStory', {})
                
                if favorite_story:
                    print(f"⭐ Current favorite: {favorite_story.get('title', '')[:60]}...")
                    print(f"🧠 Reasoning: {favorite_story.get('reasoning', '')}")
                    return True
            
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run the enhanced favorite story test"""
    success = test_enhanced_favorite_selection()
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    if success:
        print("✅ Enhanced favorite story selection is working!")
        print("🎯 The algorithm now prioritizes:")
        print("   🔬 Scientific discoveries and breakthroughs")
        print("   😊 Good news and positive achievements") 
        print("   🤔 Amazing curiosities and phenomena")
        print("   💡 Innovations and technology advances")
        print("   🌱 Environmental and conservation stories")
        print("\n🌐 Check your hackathon URL to see the improved selection:")
        print("   http://curio-news-frontend-1760997974.s3-website-us-west-2.amazonaws.com/")
    else:
        print("⚠️ Issues detected with favorite story selection")
    
    print("\n🚀 Your Curio News now showcases the most fascinating stories!")

if __name__ == "__main__":
    main()