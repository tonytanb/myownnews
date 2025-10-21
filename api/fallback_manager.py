"""
Fallback Content Manager for Curio News

This module provides fallback strategies for each content section when agents fail.
It ensures partial content delivery rather than complete failure and uses cached content
when agents fail completely.
"""

import json
import boto3
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

dynamodb = boto3.client('dynamodb')

@dataclass
class FallbackStrategy:
    """Configuration for fallback content strategy"""
    section_name: str
    priority_order: List[str]  # Order of fallback methods to try
    cache_ttl_hours: int = 24
    min_quality_score: float = 50.0
    use_demo_content: bool = True

class FallbackManager:
    """Manages fallback content strategies for all content sections"""
    
    def __init__(self, curio_table: str):
        self.curio_table = curio_table
        self.fallback_strategies = self._initialize_fallback_strategies()
        self.demo_content = self._initialize_demo_content()
        self.cache_keys = {
            'news_stories': 'cached_news_stories',
            'favorite_story': 'cached_favorite_story',
            'weekend_recommendations': 'cached_weekend_recommendations',
            'visual_enhancements': 'cached_visual_enhancements',
            'script_content': 'cached_script_content',
            'audio_metadata': 'cached_audio_metadata'
        }
    
    def get_fallback_content(self, section_name: str, failed_content: Any = None, 
                           context: Dict = None) -> Dict[str, Any]:
        """
        Get fallback content for a specific section when agent fails
        
        Args:
            section_name: Name of the content section
            failed_content: The content that failed validation (if any)
            context: Additional context for generating fallback
            
        Returns:
            Dictionary with fallback content and metadata
        """
        try:
            strategy = self.fallback_strategies.get(section_name)
            if not strategy:
                return self._create_error_fallback(section_name, "No fallback strategy configured")
            
            print(f"🔄 Generating fallback content for {section_name}")
            
            # Try each fallback method in priority order
            for method in strategy.priority_order:
                try:
                    fallback_method = getattr(self, f'_fallback_{method}')
                    result = fallback_method(section_name, failed_content, context)
                    
                    if result and result.get('content'):
                        print(f"✅ Fallback successful using method: {method}")
                        result['fallback_method'] = method
                        result['fallback_timestamp'] = datetime.utcnow().isoformat()
                        
                        # Cache successful fallback for future use
                        self._cache_fallback_content(section_name, result)
                        
                        return result
                    else:
                        print(f"⚠️ Fallback method {method} returned no content")
                        
                except Exception as e:
                    print(f"❌ Fallback method {method} failed: {e}")
                    continue
            
            # If all methods fail, return demo content
            print(f"🎭 Using demo content for {section_name}")
            return self._get_demo_content(section_name)
            
        except Exception as e:
            print(f"❌ Critical error in fallback manager: {e}")
            return self._create_error_fallback(section_name, str(e))
    
    def get_partial_content_delivery(self, successful_sections: Dict[str, Any], 
                                   failed_sections: List[str]) -> Dict[str, Any]:
        """
        Create partial content delivery when some agents succeed and others fail
        
        Args:
            successful_sections: Content from successful agents
            failed_sections: List of section names that failed
            
        Returns:
            Complete content structure with fallbacks for failed sections
        """
        try:
            print(f"🔧 Creating partial content delivery. Failed sections: {failed_sections}")
            
            complete_content = successful_sections.copy()
            fallback_metadata = {
                'partial_delivery': True,
                'successful_sections': list(successful_sections.keys()),
                'failed_sections': failed_sections,
                'fallback_sections': [],
                'delivery_timestamp': datetime.utcnow().isoformat()
            }
            
            # Generate fallback content for each failed section
            for section_name in failed_sections:
                try:
                    fallback_result = self.get_fallback_content(section_name, context=successful_sections)
                    
                    if fallback_result and fallback_result.get('content'):
                        # Map section name to appropriate content structure key
                        content_key = self._get_content_key_for_section(section_name)
                        complete_content[content_key] = fallback_result['content']
                        fallback_metadata['fallback_sections'].append(section_name)
                        
                        # Add fallback metadata to the specific section
                        if 'metadata' not in complete_content:
                            complete_content['metadata'] = {}
                        complete_content['metadata'][f'{section_name}_fallback'] = {
                            'method': fallback_result.get('fallback_method'),
                            'timestamp': fallback_result.get('fallback_timestamp'),
                            'quality_score': fallback_result.get('quality_score', 0)
                        }
                    else:
                        print(f"⚠️ Could not generate fallback for {section_name}")
                        
                except Exception as e:
                    print(f"❌ Error generating fallback for {section_name}: {e}")
            
            # Add overall fallback metadata
            complete_content['fallback_metadata'] = fallback_metadata
            
            # Ensure content has required structure
            complete_content = self._ensure_content_structure(complete_content)
            
            return complete_content
            
        except Exception as e:
            print(f"❌ Critical error in partial content delivery: {e}")
            return self._create_emergency_content()
    
    def _fallback_cached(self, section_name: str, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Use cached content from previous successful runs"""
        try:
            cache_key = self.cache_keys.get(section_name)
            if not cache_key:
                return None
            
            # Get cached content from DynamoDB
            response = dynamodb.get_item(
                TableName=self.curio_table,
                Key={
                    'pk': {'S': 'fallback_cache'},
                    'sk': {'S': cache_key}
                }
            )
            
            if 'Item' not in response:
                print(f"📭 No cached content found for {section_name}")
                return None
            
            item = response['Item']
            
            # Check if cache is still valid
            cached_at = item.get('cachedAt', {}).get('S', '')
            if cached_at:
                try:
                    cached_time = datetime.fromisoformat(cached_at.replace('Z', '+00:00'))
                    strategy = self.fallback_strategies.get(section_name)
                    ttl_hours = strategy.cache_ttl_hours if strategy else 24
                    
                    if datetime.utcnow().replace(tzinfo=cached_time.tzinfo) - cached_time > timedelta(hours=ttl_hours):
                        print(f"⏰ Cached content for {section_name} is expired")
                        return None
                except:
                    print(f"⚠️ Could not parse cache timestamp for {section_name}")
            
            # Parse cached content
            content_str = item.get('content', {}).get('S', '{}')
            try:
                cached_content = json.loads(content_str)
                quality_score = float(item.get('qualityScore', {}).get('N', '75'))
                
                return {
                    'content': cached_content,
                    'quality_score': quality_score,
                    'source': 'cached',
                    'cached_at': cached_at
                }
            except json.JSONDecodeError:
                print(f"❌ Could not parse cached content for {section_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error retrieving cached content for {section_name}: {e}")
            return None
    
    def _fallback_generated(self, section_name: str, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Generate new fallback content based on available context"""
        try:
            generator_method = getattr(self, f'_generate_fallback_{section_name}', None)
            if not generator_method:
                print(f"⚠️ No generator method for {section_name}")
                return None
            
            return generator_method(failed_content, context)
            
        except Exception as e:
            print(f"❌ Error generating fallback content for {section_name}: {e}")
            return None
    
    def _fallback_demo(self, section_name: str, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Use demo content as fallback"""
        try:
            demo_content = self.demo_content.get(section_name)
            if not demo_content:
                return None
            
            return {
                'content': demo_content,
                'quality_score': 60.0,  # Demo content gets moderate score
                'source': 'demo'
            }
            
        except Exception as e:
            print(f"❌ Error getting demo content for {section_name}: {e}")
            return None
    
    def _generate_fallback_news_stories(self, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Generate fallback news stories from available context or RSS feeds"""
        try:
            # Try to use context from successful agents
            if context and 'news_items' in context:
                existing_stories = context['news_items']
                if existing_stories and len(existing_stories) >= 3:
                    return {
                        'content': existing_stories,
                        'quality_score': 70.0,
                        'source': 'context_reuse'
                    }
            
            # Generate basic news stories from RSS feeds
            fallback_stories = [
                {
                    "title": "Technology Updates Continue to Shape Daily Life",
                    "category": "TECHNOLOGY",
                    "summary": "Latest developments in technology continue to impact how we work and communicate.",
                    "relevance_score": 0.75,
                    "selection_reason": "Fallback content - technology remains highly relevant to target audience"
                },
                {
                    "title": "Cultural Trends Evolve in Digital Age",
                    "category": "CULTURE", 
                    "summary": "Social media and digital platforms continue to influence cultural movements.",
                    "relevance_score": 0.72,
                    "selection_reason": "Fallback content - cultural trends are always relevant to Gen Z/Millennial audience"
                },
                {
                    "title": "Global Events Shape International Relations",
                    "category": "INTERNATIONAL",
                    "summary": "Ongoing international developments continue to affect global relationships.",
                    "relevance_score": 0.68,
                    "selection_reason": "Fallback content - international awareness important for informed audience"
                }
            ]
            
            return {
                'content': fallback_stories,
                'quality_score': 65.0,
                'source': 'generated_fallback'
            }
            
        except Exception as e:
            print(f"❌ Error generating fallback news stories: {e}")
            return None
    
    def _generate_fallback_favorite_story(self, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Generate fallback favorite story selection"""
        try:
            # Try to select from existing news stories
            if context and 'news_items' in context:
                stories = context['news_items']
                if stories:
                    # Select the story with highest relevance score
                    best_story = max(stories, key=lambda x: x.get('relevance_score', 0))
                    
                    reasoning = f"Selected '{best_story.get('title', 'this story')}' as today's standout piece. " \
                              f"With a relevance score of {best_story.get('relevance_score', 0):.2f}, " \
                              f"this {best_story.get('category', 'story').lower()} story represents the kind of " \
                              f"content that sparks curiosity and conversation among our audience."
                    
                    return {
                        'content': {'reasoning': reasoning},
                        'quality_score': 70.0,
                        'source': 'context_selection'
                    }
            
            # Generic fallback reasoning
            fallback_reasoning = ("Today's standout story showcases the kind of development that makes you pause and think. " 
                                "While we're working to bring you the most fascinating content, this represents the type of " 
                                "story that typically captures attention and sparks meaningful conversations.")
            
            return {
                'content': {'reasoning': fallback_reasoning},
                'quality_score': 55.0,
                'source': 'generic_fallback'
            }
            
        except Exception as e:
            print(f"❌ Error generating fallback favorite story: {e}")
            return None
    
    def _generate_fallback_weekend_recommendations(self, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Generate fallback weekend recommendations"""
        try:
            fallback_recommendations = {
                "books": [
                    {
                        "title": "Trending BookTok Recommendations",
                        "author": "Various Authors",
                        "description": "Check out the latest trending books on BookTok for engaging reads that are capturing attention.",
                        "genre": "Various"
                    }
                ],
                "movies_and_shows": [
                    {
                        "title": "Popular Streaming Content",
                        "platform": "Various Platforms",
                        "description": "Explore trending shows and movies across streaming platforms for weekend entertainment.",
                        "genre": "Various"
                    }
                ],
                "events": [
                    {
                        "name": "Local Weekend Activities",
                        "location": "Your Area",
                        "date": "This Weekend",
                        "description": "Check local event listings and community boards for activities happening in your area.",
                        "link": "https://www.eventbrite.com"
                    }
                ],
                "cultural_insights": {
                    "current_trends": "Social media continues to drive cultural conversations and entertainment choices.",
                    "recommendation_note": "These are fallback recommendations. Check our main content for personalized suggestions."
                }
            }
            
            return {
                'content': fallback_recommendations,
                'quality_score': 60.0,
                'source': 'generated_fallback'
            }
            
        except Exception as e:
            print(f"❌ Error generating fallback weekend recommendations: {e}")
            return None
    
    def _generate_fallback_visual_enhancements(self, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Generate fallback visual enhancements"""
        try:
            # Try to enhance existing news stories
            stories = []
            if context and 'news_items' in context:
                for story in context['news_items'][:3]:  # Limit to first 3 stories
                    category = story.get('category', 'news').lower()
                    title = story.get('title', 'News Story')
                    
                    # Generate contextual image URL
                    image_keywords = self._get_image_keywords(title, category)
                    image_url = f"https://source.unsplash.com/800x400/?{image_keywords}"
                    
                    enhanced_story = {
                        "title": title,
                        "media_recommendations": {
                            "images": [{"url": image_url, "alt_text": f"{category.title()} news image"}],
                            "videos": [],
                            "social_media_optimization": {
                                "hashtags": self._generate_hashtags(title, category)
                            }
                        }
                    }
                    stories.append(enhanced_story)
            
            if not stories:
                # Generic fallback
                stories = [{
                    "title": "News Content",
                    "media_recommendations": {
                        "images": [{"url": "https://source.unsplash.com/800x400/?news,abstract", "alt_text": "News image"}],
                        "videos": [],
                        "social_media_optimization": {"hashtags": ["#News", "#Update"]}
                    }
                }]
            
            return {
                'content': {'stories': stories},
                'quality_score': 65.0,
                'source': 'generated_fallback'
            }
            
        except Exception as e:
            print(f"❌ Error generating fallback visual enhancements: {e}")
            return None
    
    def _generate_fallback_script_content(self, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Generate fallback script content"""
        try:
            # Try to create script from existing news stories
            if context and 'news_items' in context:
                stories = context['news_items'][:3]  # Use first 3 stories
                
                script_parts = ["Hey there! Here's what's happening today."]
                
                for i, story in enumerate(stories):
                    title = story.get('title', 'A story')
                    summary = story.get('summary', 'An interesting development')
                    
                    if i == 0:
                        script_parts.append(f"First up, {title.lower()}. {summary}")
                    elif i == len(stories) - 1:
                        script_parts.append(f"And finally, {title.lower()}. {summary}")
                    else:
                        script_parts.append(f"Next, {title.lower()}. {summary}")
                
                script_parts.append("That's your update for now. Stay curious!")
                
                script = " ".join(script_parts)
                
                return {
                    'content': script,
                    'quality_score': 65.0,
                    'source': 'context_generated'
                }
            
            # Generic fallback script
            fallback_script = ("Hey there! We're working on bringing you the latest news that matters to you. " 
                             "While our AI agents are preparing fresh content, we wanted to make sure you know " 
                             "we're here and working to keep you informed about the stories that shape our world. " 
                             "Check back soon for your personalized news briefing!")
            
            return {
                'content': fallback_script,
                'quality_score': 50.0,
                'source': 'generic_fallback'
            }
            
        except Exception as e:
            print(f"❌ Error generating fallback script content: {e}")
            return None
    
    def _generate_fallback_audio_metadata(self, failed_content: Any, context: Dict) -> Dict[str, Any]:
        """Generate fallback audio metadata"""
        try:
            # Use demo audio URL and generate basic word timings
            demo_audio_url = "https://myownnews-mvp-assetsbucket-kozbz1eooh6q.s3.us-west-2.amazonaws.com/audio/2025-10-18/voice-1760748904-6b6190bc.mp3"
            
            # Generate basic word timings if script is available
            word_timings = []
            if context and 'script' in context:
                script = context['script']
                words = script.split()[:50]  # Limit to first 50 words
                
                for i, word in enumerate(words):
                    word_timings.append({
                        'word': word,
                        'start': round(i * 0.4, 2),
                        'end': round((i + 1) * 0.4, 2)
                    })
            
            return {
                'content': {
                    'audio_url': demo_audio_url,
                    'word_timings': word_timings
                },
                'quality_score': 60.0,
                'source': 'demo_with_generated_timings'
            }
            
        except Exception as e:
            print(f"❌ Error generating fallback audio metadata: {e}")
            return None
    
    def _cache_fallback_content(self, section_name: str, fallback_result: Dict[str, Any]):
        """Cache successful fallback content for future use"""
        try:
            cache_key = self.cache_keys.get(section_name)
            if not cache_key:
                return
            
            item = {
                'pk': {'S': 'fallback_cache'},
                'sk': {'S': cache_key},
                'content': {'S': json.dumps(fallback_result['content'], ensure_ascii=False)},
                'qualityScore': {'N': str(fallback_result.get('quality_score', 50.0))},
                'cachedAt': {'S': datetime.utcnow().isoformat()},
                'fallbackMethod': {'S': fallback_result.get('fallback_method', 'unknown')},
                'expiresAt': {'N': str(int(time.time()) + (24 * 3600))}  # 24 hour TTL
            }
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            print(f"💾 Cached fallback content for {section_name}")
            
        except Exception as e:
            print(f"❌ Error caching fallback content for {section_name}: {e}")
    
    def _get_content_key_for_section(self, section_name: str) -> str:
        """Map section name to content structure key"""
        mapping = {
            'news_stories': 'news_items',
            'favorite_story': 'agentOutputs.favoriteStory',
            'weekend_recommendations': 'agentOutputs.weekendRecommendations',
            'visual_enhancements': 'agentOutputs.mediaEnhancements',
            'script_content': 'script',
            'audio_metadata': 'audioUrl'  # This is more complex, handled specially
        }
        return mapping.get(section_name, section_name)
    
    def _ensure_content_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure content has the required structure for the frontend"""
        # Ensure agentOutputs structure exists
        if 'agentOutputs' not in content:
            content['agentOutputs'] = {}
        
        # Ensure basic fields exist
        required_fields = {
            'news_items': [],
            'script': '',
            'audioUrl': '',
            'word_timings': [],
            'sources': ['Fallback Content'],
            'generatedAt': datetime.utcnow().isoformat(),
            'why': 'Content generated with fallback mechanisms due to agent failures'
        }
        
        for field, default_value in required_fields.items():
            if field not in content:
                content[field] = default_value
        
        return content
    
    def _create_emergency_content(self) -> Dict[str, Any]:
        """Create emergency content when all fallback methods fail"""
        return {
            'news_items': [
                {
                    "title": "Curio News System Update",
                    "category": "SYSTEM",
                    "summary": "Our AI agents are currently updating to bring you better content. Please check back soon.",
                    "relevance_score": 1.0
                }
            ],
            'script': "Hey there! Our AI news agents are currently updating to bring you even better content. We'll be back with your personalized news briefing soon!",
            'audioUrl': '',
            'word_timings': [],
            'sources': ['System Update'],
            'generatedAt': datetime.utcnow().isoformat(),
            'why': 'Emergency content - system is updating',
            'agentOutputs': {
                'favoriteStory': {
                    'reasoning': 'System is currently updating to provide better story selection.'
                },
                'weekendRecommendations': {
                    'books': [],
                    'movies_and_shows': [],
                    'events': [],
                    'cultural_insights': {
                        'system_status': 'Updating to provide better recommendations'
                    }
                },
                'mediaEnhancements': {
                    'stories': []
                }
            },
            'emergency_mode': True,
            'fallback_metadata': {
                'emergency_content': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def _create_error_fallback(self, section_name: str, error_message: str) -> Dict[str, Any]:
        """Create error fallback when section-specific fallback fails"""
        return {
            'content': None,
            'error': error_message,
            'quality_score': 0.0,
            'source': 'error',
            'section': section_name,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_image_keywords(self, title: str, category: str) -> str:
        """Generate image keywords for fallback visual content"""
        title_lower = title.lower()
        
        # Specific keyword mapping
        if any(word in title_lower for word in ['ai', 'artificial', 'intelligence']):
            return 'artificial-intelligence,technology,computer'
        elif any(word in title_lower for word in ['startup', 'business']):
            return 'startup,business,office'
        elif any(word in title_lower for word in ['politics', 'government']):
            return 'government,politics,law'
        
        # Category-based keywords
        category_keywords = {
            'technology': 'technology,computer,innovation',
            'business': 'business,finance,office',
            'politics': 'politics,government,law',
            'science': 'science,research,laboratory',
            'culture': 'culture,art,entertainment',
            'international': 'world,global,international'
        }
        
        return category_keywords.get(category.lower(), 'news,abstract,modern')
    
    def _generate_hashtags(self, title: str, category: str) -> List[str]:
        """Generate hashtags for social media optimization"""
        hashtags = [f"#{category}"]
        
        title_lower = title.lower()
        if 'ai' in title_lower or 'artificial' in title_lower:
            hashtags.extend(['#AI', '#Technology'])
        elif 'startup' in title_lower:
            hashtags.extend(['#Startup', '#Business'])
        elif 'politics' in title_lower:
            hashtags.extend(['#Politics', '#News'])
        else:
            hashtags.extend(['#News', '#Update'])
        
        return hashtags[:4]  # Limit to 4 hashtags
    
    def _initialize_fallback_strategies(self) -> Dict[str, FallbackStrategy]:
        """Initialize fallback strategies for each content section"""
        return {
            'news_stories': FallbackStrategy(
                section_name='news_stories',
                priority_order=['cached', 'generated', 'demo'],
                cache_ttl_hours=12,
                min_quality_score=60.0
            ),
            'favorite_story': FallbackStrategy(
                section_name='favorite_story',
                priority_order=['cached', 'generated', 'demo'],
                cache_ttl_hours=24,
                min_quality_score=55.0
            ),
            'weekend_recommendations': FallbackStrategy(
                section_name='weekend_recommendations',
                priority_order=['cached', 'generated', 'demo'],
                cache_ttl_hours=48,  # Weekend content can be cached longer
                min_quality_score=50.0
            ),
            'visual_enhancements': FallbackStrategy(
                section_name='visual_enhancements',
                priority_order=['generated', 'cached', 'demo'],
                cache_ttl_hours=24,
                min_quality_score=55.0
            ),
            'script_content': FallbackStrategy(
                section_name='script_content',
                priority_order=['generated', 'cached', 'demo'],
                cache_ttl_hours=6,  # Script should be fresh
                min_quality_score=60.0
            ),
            'audio_metadata': FallbackStrategy(
                section_name='audio_metadata',
                priority_order=['generated', 'demo', 'cached'],
                cache_ttl_hours=12,
                min_quality_score=50.0
            )
        }
    
    def _initialize_demo_content(self) -> Dict[str, Any]:
        """Initialize demo content for each section"""
        return {
            'news_stories': [
                {
                    "title": "Demo: AI Technology Advances Continue",
                    "category": "TECHNOLOGY",
                    "summary": "This is demo content showing how our system handles technology news.",
                    "relevance_score": 0.8,
                    "selection_reason": "Demo content for system testing"
                },
                {
                    "title": "Demo: Cultural Trends Shape Digital Landscape",
                    "category": "CULTURE",
                    "summary": "This is demo content showing how our system handles cultural news.",
                    "relevance_score": 0.75,
                    "selection_reason": "Demo content for system testing"
                }
            ],
            'favorite_story': {
                'reasoning': 'This is demo content showing how our AI selects and explains the most fascinating story of the day.'
            },
            'weekend_recommendations': {
                "books": [
                    {
                        "title": "Demo Book Recommendation",
                        "author": "Demo Author",
                        "description": "This is demo content showing how our system recommends books.",
                        "genre": "Demo"
                    }
                ],
                "movies_and_shows": [
                    {
                        "title": "Demo Show Recommendation",
                        "platform": "Demo Platform",
                        "description": "This is demo content showing how our system recommends shows.",
                        "genre": "Demo"
                    }
                ],
                "events": [
                    {
                        "name": "Demo Event",
                        "location": "Demo Location",
                        "date": "Demo Date",
                        "description": "This is demo content showing how our system recommends events."
                    }
                ]
            },
            'visual_enhancements': {
                'stories': [
                    {
                        "title": "Demo Enhanced Story",
                        "media_recommendations": {
                            "images": [{"url": "https://source.unsplash.com/800x400/?demo,news", "alt_text": "Demo image"}],
                            "social_media_optimization": {"hashtags": ["#Demo", "#News"]}
                        }
                    }
                ]
            },
            'script_content': "Hey there! This is demo content showing how our AI creates engaging scripts for audio news. We're working to bring you the most relevant and interesting stories!",
            'audio_metadata': {
                'audio_url': 'https://myownnews-mvp-assetsbucket-kozbz1eooh6q.s3.us-west-2.amazonaws.com/audio/2025-10-18/voice-1760748904-6b6190bc.mp3',
                'word_timings': [
                    {"word": "Hey", "start": 0.0, "end": 0.3},
                    {"word": "there!", "start": 0.3, "end": 0.7}
                ]
            }
        }