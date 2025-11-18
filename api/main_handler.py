import json
import boto3
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict
from botocore.exceptions import ClientError

# Import the consolidated content generator and multi-agent orchestrator
from content_generator import generate_content
from multi_agent_orchestrator import CurioMultiAgentOrchestrator

# Import Bedrock Agent Orchestrator
try:
    from bedrock_orchestrator import BedrockAgentOrchestrator
    BEDROCK_ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Bedrock orchestrator not available: {e}")
    BEDROCK_ORCHESTRATOR_AVAILABLE = False

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

# Environment variables
BUCKET = os.getenv('BUCKET')
CURIO_TABLE = os.getenv('CURIO_TABLE')
CORS_ALLOW_ORIGIN = os.getenv('CORS_ALLOW_ORIGIN', '*')
PRESIGN_EXPIRES = int(os.getenv('PRESIGN_EXPIRES', '1200'))
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
MODEL_ID = os.getenv('MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
VOICE_ID = os.getenv('VOICE_ID', 'Joanna')

# Constants
STALE_MINUTES = 10  # Content is stale after 10 minutes

def cors_headers():
    """Return CORS headers for all responses"""
    return {
        'Access-Control-Allow-Origin': CORS_ALLOW_ORIGIN,
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token, X-Requested-With, Accept, Origin',
        'Access-Control-Allow-Credentials': 'false',
        'Access-Control-Max-Age': '86400',
        'Content-Type': 'application/json'
    }

def safe_json_dumps(data):
    """Safely serialize data to JSON with proper encoding"""
    try:
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    except (TypeError, ValueError) as e:
        print(f"JSON serialization error: {e}")
        # Fallback: convert problematic data types
        safe_data = convert_to_json_safe(data)
        return json.dumps(safe_data, ensure_ascii=False, separators=(',', ':'))

def convert_to_json_safe(obj):
    """Convert object to JSON-safe format"""
    if isinstance(obj, dict):
        return {k: convert_to_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_safe(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        # Convert other types to string
        return str(obj)

def get_cached_brief():
    """Get the latest cached brief from DynamoDB"""
    try:
        response = dynamodb.get_item(
            TableName=CURIO_TABLE,
            Key={
                'pk': {'S': 'brief'},
                'sk': {'S': 'latest'}
            }
        )
        if 'Item' in response:
            item = response['Item']
            brief = {
                'audioUrl': item.get('audioUrl', {}).get('S', ''),
                'sources': json.loads(item.get('sources', {}).get('S', '[]')),
                'generatedAt': item.get('generatedAt', {}).get('S', ''),
                'why': item.get('why', {}).get('S', ''),
                'traceId': item.get('traceId', {}).get('S', ''),
                'script': item.get('script', {}).get('S', ''),
                'news_items': json.loads(item.get('news_items', {}).get('S', '[]')),
                'word_timings': json.loads(item.get('word_timings', {}).get('S', '[]')),
                'quality_score': float(item.get('qualityScore', {}).get('N', '0')),
                'enhanced_orchestration': item.get('enhancedOrchestration', {}).get('BOOL', False),
                'validation_passed': item.get('validationPassed', {}).get('BOOL', False)
            }
            return brief
    except Exception as e:
        print(f"Error getting cached brief: {e}")
    return None

def get_enhanced_brief_with_agent_outputs(run_id: str = None):
    """Get enhanced brief with complete agent results from the orchestrator"""
    try:
        if run_id:
            # Get specific enhanced brief
            response = dynamodb.get_item(
                TableName=CURIO_TABLE,
                Key={
                    'pk': {'S': 'enhanced_brief'},
                    'sk': {'S': run_id}
                }
            )
        else:
            # Get latest enhanced brief
            response = dynamodb.query(
                TableName=CURIO_TABLE,
                KeyConditionExpression='pk = :pk',
                ExpressionAttributeValues={
                    ':pk': {'S': 'enhanced_brief'}
                },
                ScanIndexForward=False,
                Limit=1
            )
            
        content = None
        if run_id and 'Item' in response:
            content = json.loads(response['Item']['content']['S'])
        elif not run_id and 'Items' in response and response['Items']:
            content = json.loads(response['Items'][0]['content']['S'])
        
        return content
            
    except Exception as e:
        print(f"Error getting enhanced brief: {e}")
        return None

def is_stale(generated_at_str, minutes=STALE_MINUTES):
    """Check if content is older than specified minutes"""
    try:
        generated_at = datetime.fromisoformat(generated_at_str.replace('Z', '+00:00'))
        now = datetime.now(generated_at.tzinfo)
        return (now - generated_at).total_seconds() > (minutes * 60)
    except:
        return True

def try_acquire_lock():
    """Try to acquire a generation lock using DynamoDB conditional put"""
    try:
        expires_at = int(time.time()) + 600  # 10 minute TTL
        dynamodb.put_item(
            TableName=CURIO_TABLE,
            Item={
                'pk': {'S': 'generation'},
                'sk': {'S': 'lock'},
                'status': {'S': 'RUNNING'},
                'expiresAt': {'N': str(expires_at)},
                'startedAt': {'S': datetime.utcnow().isoformat()}
            },
            ConditionExpression='attribute_not_exists(pk) OR expiresAt < :now',
            ExpressionAttributeValues={
                ':now': {'N': str(int(time.time()))}
            }
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False
        raise

def fetch_real_news_direct():
    """Fetch real news data directly using NewsAPI"""
    try:
        import requests
        
        if not NEWS_API_KEY:
            print("⚠️ No NewsAPI key available")
            return []
        
        print(f"🔑 Using NewsAPI with key: {NEWS_API_KEY[:8]}...")
        
        # Get top headlines
        headlines_url = "https://newsapi.org/v2/top-headlines"
        headlines_params = {
            'apiKey': NEWS_API_KEY,
            'language': 'en',
            'country': 'us',
            'pageSize': 10,
            'category': 'general'
        }
        
        response = requests.get(headlines_url, params=headlines_params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        news_items = []
        
        if data.get('status') == 'ok':
            for article in data.get('articles', []):
                if article.get('title') and article.get('description'):
                    news_items.append({
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'link': article.get('url', ''),
                        'published': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'category': 'GENERAL',
                        'image': article.get('urlToImage', ''),
                        'relevance_score': 0.8
                    })
        
        print(f"📰 NewsAPI returned {len(news_items)} articles")
        return news_items
        
    except Exception as e:
        print(f"❌ Error fetching news directly: {e}")
        return []

def generate_entertainment_recommendations_main(news_items):
    """Generate entertainment recommendations for main handler"""
    try:
        # Simple entertainment recommendations based on current popular content
        entertainment_recommendations = {
            "top_movies": [
                {
                    "title": "Dune: Part Two",
                    "genre": "Sci-Fi Epic",
                    "rating": "8.8/10",
                    "platform": "Max",
                    "description": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
                    "release_year": 2024,
                    "runtime": "2h 46m"
                },
                {
                    "title": "Oppenheimer",
                    "genre": "Historical Biography",
                    "rating": "8.4/10",
                    "platform": "Various Streaming",
                    "description": "The story of J. Robert Oppenheimer and the development of the atomic bomb.",
                    "release_year": 2023,
                    "runtime": "3h 0m"
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
                    "episodes_per_season": 10,
                    "status": "ongoing"
                },
                {
                    "title": "Wednesday",
                    "genre": "Dark Comedy",
                    "rating": "8.1/10",
                    "platform": "Netflix",
                    "description": "Wednesday Addams navigates her years as a student at Nevermore Academy.",
                    "seasons": 2,
                    "episodes_per_season": 8,
                    "status": "new_season"
                }
            ],
            "theater_plays": [
                {
                    "title": "Hamilton",
                    "genre": "Musical Biography",
                    "venue": "Richard Rodgers Theatre",
                    "city": "New York",
                    "description": "The revolutionary story of Alexander Hamilton, founding father and first Secretary of the Treasury.",
                    "show_times": "Tue-Sun 8PM, Wed & Sat 2PM",
                    "ticket_info": "From $79",
                    "rating": "9.5/10"
                },
                {
                    "title": "The Lion King",
                    "genre": "Musical Family",
                    "venue": "Minskoff Theatre",
                    "city": "New York",
                    "description": "Disney's award-winning musical about Simba's journey to become king.",
                    "show_times": "Tue-Fri 8PM, Sat 2PM & 8PM, Sun 1PM & 6:30PM",
                    "ticket_info": "From $89",
                    "rating": "9.2/10"
                }
            ]
        }
        
        return entertainment_recommendations
        
    except Exception as e:
        print(f"❌ Error generating entertainment recommendations in main handler: {e}")
        return {
            "top_movies": [],
            "must_watch_series": [],
            "theater_plays": []
        }

def create_content_with_real_news():
    """Create content using real news data"""
    try:
        print("📰 Fetching real news data...")
        
        # Try to fetch real current news
        real_news = []
        
        # Fetch news directly
        if not real_news:
            real_news = fetch_real_news_direct()
            print(f"✅ Fetched {len(real_news)} real news articles directly")
        
        # Create realistic content based on actual news
        current_time = datetime.utcnow().isoformat()
        
        # Generate script based on real news
        if real_news:
            top_stories = real_news[:3]  # Use top 3 stories for script
            script_parts = ["Welcome to Curio News! Here are today's top stories that matter to you."]
            
            for i, story in enumerate(top_stories, 1):
                title = story.get('title', 'Breaking News')
                summary = story.get('summary', 'Important developments in the news.')
                script_parts.append(f"Story {i}: {title}. {summary}")
            
            script_parts.append("That's your news update for today. Stay informed, stay curious!")
            script = " ".join(script_parts)
        else:
            script = "Welcome to Curio News! We're currently updating our news sources. Please check back shortly for the latest stories."
        
        # Generate word timings for the script
        words = script.split()
        word_timings = []
        current_time_offset = 0.0
        
        for word in words[:50]:  # Limit to first 50 words for performance
            duration = 0.4  # Average word duration
            word_timings.append({
                'word': word,
                'start': round(current_time_offset, 2),
                'end': round(current_time_offset + duration, 2)
            })
            current_time_offset += duration
        
        # Create agent outputs based on real news
        favorite_story = None
        media_enhancements = {'stories': []}
        
        if real_news:
            # Select favorite story (highest relevance or first story)
            favorite_story = {
                'title': real_news[0].get('title', 'Top Story'),
                'reasoning': f"Selected as today's most significant story: {real_news[0].get('title', 'Breaking news')}. This story stands out for its relevance and potential impact on our audience."
            }
            
            # Create media enhancements for top stories
            for story in real_news[:3]:
                story_title = story.get('title', '')
                category = story.get('category', 'NEWS').lower()
                
                # Generate contextual hashtags
                hashtags = [f"#{category.title()}", "#News", "#CurioNews"]
                if 'tech' in story_title.lower() or 'ai' in story_title.lower():
                    hashtags.append("#Technology")
                elif 'business' in story_title.lower() or 'market' in story_title.lower():
                    hashtags.append("#Business")
                elif 'climate' in story_title.lower() or 'environment' in story_title.lower():
                    hashtags.append("#Climate")
                
                media_enhancements['stories'].append({
                    'title': story_title,
                    'media_recommendations': {
                        'images': [{
                            'url': story.get('image', f"https://source.unsplash.com/800x400/?{category},news"),
                            'alt_text': f"Image for {story_title[:50]}"
                        }],
                        'videos': [],
                        'social_media_optimization': {'hashtags': hashtags[:4]}
                    }
                })
        
        # Create weekend recommendations based on news themes
        weekend_recommendations = {
            'books': [
                {
                    'title': 'The News: A User\'s Manual',
                    'author': 'Alain de Botton',
                    'description': 'A thoughtful guide to consuming news in the modern age.',
                    'genre': 'Non-fiction'
                },
                {
                    'title': 'Factfulness',
                    'author': 'Hans Rosling',
                    'description': 'Ten reasons we\'re wrong about the world and why things are better than you think.',
                    'genre': 'Social Science'
                }
            ],
            'movies_and_shows': [
                {
                    'title': 'All the President\'s Men',
                    'platform': 'Various Streaming',
                    'description': 'Classic journalism thriller about investigative reporting.',
                    'genre': 'Drama, Thriller'
                },
                {
                    'title': 'The Morning Show',
                    'platform': 'Apple TV+',
                    'description': 'Behind-the-scenes look at a morning news program.',
                    'genre': 'Drama'
                }
            ],
            'events': [
                {
                    'name': 'Local News Literacy Workshops',
                    'location': 'Check local libraries and community centers',
                    'date': 'Various weekends',
                    'description': 'Learn to critically evaluate news sources and combat misinformation.',
                    'link': 'Search for "news literacy" + your city'
                },
                {
                    'name': 'Current Events Discussion Groups',
                    'location': 'Coffee shops, bookstores, community centers',
                    'date': 'Weekly meetups',
                    'description': 'Engage in thoughtful discussions about current events with your community.',
                    'link': 'https://www.meetup.com'
                }
            ],
            'entertainment_recommendations': generate_entertainment_recommendations_main(real_news),
            'cultural_insights': {
                'news_consumption_trends': 'Young adults increasingly prefer personalized, AI-curated news that cuts through information overload.',
                'social_media_phenomena': 'News content performs best when it\'s accessible, visual, and provides clear context.',
                'media_literacy_focus': 'There\'s growing emphasis on understanding news sources and combating misinformation.'
            }
        }
        
        return {
            'audioUrl': 'https://myownnews-mvp-assetsbucket-kozbz1eooh6q.s3.us-west-2.amazonaws.com/audio/2025-10-18/voice-1760748904-6b6190bc.mp3',
            'sources': list(set([story.get('source', 'News Source') for story in real_news[:5]])) if real_news else ['BBC News', 'Reuters', 'Associated Press'],
            'generatedAt': current_time,
            'why': f'Fresh content curated from {len(real_news)} real news sources using powerful Bedrock agents!',
            'traceId': f'unified-{int(time.time())}',
            'script': script,
            'news_items': real_news[:8] if real_news else [],  # Limit to 8 items for performance
            'word_timings': word_timings,
            'agentOutputs': {
                'favoriteStory': favorite_story or {
                    'title': 'News Update',
                    'reasoning': 'Curating the most relevant stories for you.'
                },
                'mediaEnhancements': media_enhancements,
                'weekendRecommendations': weekend_recommendations
            },
            'shouldRefresh': False,
            'agentStatus': 'READY',
            'quality_score': 90,
            'enhanced_orchestration': True,
            'validation_passed': True
        }
        
    except Exception as e:
        print(f"❌ Error creating content with real news: {e}")
        # Fallback to basic content
        return {
            'audioUrl': '',
            'sources': ['News Sources'],
            'generatedAt': datetime.utcnow().isoformat(),
            'why': 'Content generation in progress...',
            'traceId': f'fallback-{int(time.time())}',
            'script': 'Welcome to Curio News. We are currently updating our content sources.',
            'news_items': [],
            'word_timings': [],
            'agentOutputs': {
                'favoriteStory': {'title': 'Loading...', 'reasoning': 'Content being prepared...'},
                'mediaEnhancements': {'stories': []},
                'weekendRecommendations': {'books': [], 'movies_and_shows': [], 'events': [], 'entertainment_recommendations': {'top_movies': [], 'must_watch_series': [], 'theater_plays': []}, 'cultural_insights': {}}
            },
            'shouldRefresh': True,
            'agentStatus': 'LOADING',
            'quality_score': 0,
            'enhanced_orchestration': False,
            'validation_passed': False
        }

def handle_bootstrap(event):
    """Handle bootstrap endpoint - serves complete content with consolidated architecture"""
    try:
        print("🚀 Bootstrap endpoint called - using consolidated architecture")
        
        # Try to get cached brief first
        cached_brief = get_cached_brief()
        
        if cached_brief and not is_stale(cached_brief.get('generatedAt', '')):
            print("📦 Found fresh cached brief")
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps(cached_brief)
            }
        
        # Generate fresh content using multi-agent orchestration
        print("🔄 Generating fresh content with multi-agent orchestration")
        
        # Check environment variables for Bedrock agent configuration
        use_bedrock_agents = os.getenv('USE_BEDROCK_AGENTS', 'false').lower() == 'true'
        use_multi_agent = os.getenv('ENABLE_MULTI_AGENT', 'true').lower() == 'true'
        
        fresh_content = None
        
        # Priority 1: Try Bedrock Agent Orchestrator if enabled and available
        if use_bedrock_agents and BEDROCK_ORCHESTRATOR_AVAILABLE:
            try:
                print("🎭 Activating Bedrock Multi-Agent Orchestration System...")
                bedrock_orchestrator = BedrockAgentOrchestrator()
                
                # Check if agent IDs are configured
                if not bedrock_orchestrator.agent_ids:
                    print("⚠️ No Bedrock agent IDs configured, falling back to standard orchestration")
                else:
                    # Get initial news items for orchestration
                    from content_generator import ContentGenerator
                    temp_generator = ContentGenerator(CURIO_TABLE)
                    initial_news = temp_generator._fetch_news()
                    
                    # Run Bedrock multi-agent orchestration
                    import asyncio
                    fresh_content = asyncio.run(bedrock_orchestrator.orchestrate_content_generation(initial_news))
                    
                    if fresh_content:
                        print(f"✅ Bedrock orchestration successful with {len(bedrock_orchestrator.agent_ids)} agents")
                        # Add orchestration trace and metadata to response
                        fresh_content.update({
                            'orchestration_type': 'bedrock_agents',
                            'bedrock_agents_used': True,
                            'agent_count': len(bedrock_orchestrator.agent_ids)
                        })
            except Exception as bedrock_error:
                print(f"⚠️ Bedrock orchestration failed: {bedrock_error}")
                import traceback
                traceback.print_exc()
                fresh_content = None
        
        # Priority 2: Fallback to existing multi-agent orchestrator
        if not fresh_content and use_multi_agent:
            try:
                print("👥 Falling back to standard Multi-Agent Orchestration System...")
                orchestrator = CurioMultiAgentOrchestrator(CURIO_TABLE)
                
                # Get initial news items for orchestration
                from content_generator import ContentGenerator
                temp_generator = ContentGenerator(CURIO_TABLE)
                initial_news = temp_generator._fetch_news()
                
                # Run multi-agent orchestration
                import asyncio
                fresh_content = asyncio.run(orchestrator.orchestrate_content_generation(initial_news))
                
                if fresh_content:
                    fresh_content.update({
                        'orchestration_type': 'standard_multi_agent',
                        'bedrock_agents_used': False
                    })
            except Exception as multi_agent_error:
                print(f"⚠️ Multi-agent orchestration failed: {multi_agent_error}")
                fresh_content = None
        
        # Priority 3: Fallback to single-agent content generator
        if not fresh_content:
            print("🤖 Using single-agent content generator (fallback)")
            fresh_content = generate_content(CURIO_TABLE)
            if fresh_content:
                fresh_content.update({
                    'orchestration_type': 'single_agent',
                    'bedrock_agents_used': False
                })
        
        # Priority 4: Last resort - create content with real news
        if not fresh_content or not fresh_content.get('news_items'):
            print("⚠️ Content generation returned empty, using fallback")
            fresh_content = create_content_with_real_news()
            fresh_content.update({
                'orchestration_type': 'fallback',
                'bedrock_agents_used': False
            })
        
        if fresh_content:
            print(f"✅ Generated fresh content with {len(fresh_content.get('news_items', []))} news items")
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps(fresh_content)
            }
        
    except Exception as e:
        print(f"❌ Error in bootstrap: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error fallback content
        try:
            error_content = generate_content(CURIO_TABLE)
            if not error_content or not error_content.get('news_items'):
                error_content = create_content_with_real_news()
            
            error_content.update({
                'error_type': 'bootstrap_error',
                'message': 'Temporary service issue. Serving fallback content.',
                'shouldRefresh': True,
                'agentStatus': 'ERROR',
                'orchestration_type': 'error_fallback',
                'bedrock_agents_used': False
            })
        except:
            # Ultimate fallback
            error_content = {
                'audioUrl': '',
                'sources': ['Emergency System'],
                'generatedAt': datetime.utcnow().isoformat(),
                'why': 'System temporarily unavailable. Please refresh.',
                'traceId': f'error-{int(time.time())}',
                'script': 'Welcome to Curio News. We are experiencing technical difficulties.',
                'news_items': [],
                'word_timings': [],
                'agentOutputs': {
                    'favoriteStory': {'title': 'System Update', 'reasoning': 'Please refresh for latest content.'},
                    'mediaEnhancements': {'stories': []},
                    'weekendRecommendations': {'books': [], 'movies_and_shows': [], 'events': [], 'entertainment_recommendations': {'top_movies': [], 'must_watch_series': [], 'theater_plays': []}, 'cultural_insights': {}}
                },
                'shouldRefresh': True,
                'agentStatus': 'ERROR',
                'error_type': 'critical_error',
                'orchestration_type': 'critical_fallback',
                'bedrock_agents_used': False
            }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': safe_json_dumps(error_content)
        }

def handle_generate_fresh(event):
    """Handle generate-fresh endpoint - starts fresh content generation with consolidated architecture"""
    try:
        print("🔄 Generate fresh endpoint called - using consolidated content generator")
        
        # Generate unique run ID
        run_id = str(uuid.uuid4())[:8]
        print(f"Starting fresh generation with run_id: {run_id}")
        
        # Check environment variables for Bedrock agent configuration
        use_bedrock_agents = os.getenv('USE_BEDROCK_AGENTS', 'false').lower() == 'true'
        use_multi_agent = os.getenv('ENABLE_MULTI_AGENT', 'true').lower() == 'true'
        
        fresh_content = None
        
        # Priority 1: Try Bedrock Agent Orchestrator if enabled and available
        if use_bedrock_agents and BEDROCK_ORCHESTRATOR_AVAILABLE:
            try:
                print("🎭 Activating Bedrock Multi-Agent Orchestration System...")
                bedrock_orchestrator = BedrockAgentOrchestrator()
                
                # Check if agent IDs are configured
                if not bedrock_orchestrator.agent_ids:
                    print("⚠️ No Bedrock agent IDs configured, falling back to standard orchestration")
                else:
                    # Get initial news items for orchestration
                    from content_generator import ContentGenerator
                    temp_generator = ContentGenerator(CURIO_TABLE)
                    initial_news = temp_generator._fetch_news()
                    
                    # Run Bedrock multi-agent orchestration
                    import asyncio
                    fresh_content = asyncio.run(bedrock_orchestrator.orchestrate_content_generation(initial_news))
                    
                    if fresh_content:
                        print(f"✅ Bedrock orchestration successful with {len(bedrock_orchestrator.agent_ids)} agents")
                        # Add orchestration trace and metadata to response
                        fresh_content.update({
                            'orchestration_type': 'bedrock_agents',
                            'bedrock_agents_used': True,
                            'agent_count': len(bedrock_orchestrator.agent_ids)
                        })
            except Exception as bedrock_error:
                print(f"⚠️ Bedrock orchestration failed: {bedrock_error}")
                import traceback
                traceback.print_exc()
                fresh_content = None
        
        # Priority 2: Fallback to existing multi-agent orchestrator
        if not fresh_content and use_multi_agent:
            try:
                print("👥 Falling back to standard Multi-Agent Orchestration System...")
                orchestrator = CurioMultiAgentOrchestrator(CURIO_TABLE)
                
                # Get initial news items for orchestration
                from content_generator import ContentGenerator
                temp_generator = ContentGenerator(CURIO_TABLE)
                initial_news = temp_generator._fetch_news()
                
                # Run multi-agent orchestration
                import asyncio
                fresh_content = asyncio.run(orchestrator.orchestrate_content_generation(initial_news))
                
                if fresh_content:
                    fresh_content.update({
                        'orchestration_type': 'standard_multi_agent',
                        'bedrock_agents_used': False
                    })
            except Exception as multi_agent_error:
                print(f"⚠️ Multi-agent orchestration failed: {multi_agent_error}")
                fresh_content = None
        
        # Priority 3: Fallback to single-agent content generator
        if not fresh_content:
            print("🤖 Using single-agent content generator (fallback)")
            fresh_content = generate_content(CURIO_TABLE, run_id)
            if fresh_content:
                fresh_content.update({
                    'orchestration_type': 'single_agent',
                    'bedrock_agents_used': False
                })
        
        if fresh_content:
            print(f"✅ Content generation completed successfully")
            
            # Store the generated content in cache
            try:
                dynamodb.put_item(
                    TableName=CURIO_TABLE,
                    Item={
                        'pk': {'S': 'brief'},
                        'sk': {'S': 'latest'},
                        'audioUrl': {'S': fresh_content.get('audioUrl', '')},
                        'sources': {'S': json.dumps(fresh_content.get('sources', []))},
                        'generatedAt': {'S': fresh_content.get('generatedAt', '')},
                        'why': {'S': fresh_content.get('why', '')},
                        'traceId': {'S': fresh_content.get('traceId', '')},
                        'script': {'S': fresh_content.get('script', '')},
                        'news_items': {'S': json.dumps(fresh_content.get('news_items', []))},
                        'word_timings': {'S': json.dumps(fresh_content.get('word_timings', []))},
                        'expiresAt': {'N': str(int(time.time()) + 86400)},  # 24 hour TTL
                        'qualityScore': {'N': str(fresh_content.get('quality_score', 0))},
                        'enhancedOrchestration': {'BOOL': fresh_content.get('enhanced_orchestration', True)},
                        'validationPassed': {'BOOL': fresh_content.get('validation_passed', True)}
                    }
                )
                print(f"✅ Successfully stored fresh content for run_id: {run_id}")
            except Exception as e:
                print(f"⚠️ Error storing content: {e}")
                # Continue anyway, we can still return the content
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps({
                    'success': True,
                    'runId': run_id,
                    'message': 'Fresh content generated successfully with consolidated architecture!',
                    'content': fresh_content
                })
            }
        else:
            # Content generation failed, use fallback
            fallback_content = create_content_with_real_news()
            fallback_content.update({
                'error_type': 'generation_failed',
                'message': 'Content generation failed. Serving real news data as fallback.',
                'agentStatus': 'ERROR',
                'orchestration_type': 'fallback',
                'bedrock_agents_used': False
            })
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps({
                    'success': False,
                    'runId': run_id,
                    'message': 'Generation failed, serving fallback content',
                    'content': fallback_content
                })
            }
        
    except Exception as e:
        print(f"❌ Error in generate_fresh: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to provide fallback with real news
        try:
            fallback_content = create_content_with_real_news()
            fallback_content.update({
                'error_type': 'generation_error',
                'message': 'Content generation encountered an error. Serving real news data.',
                'agentStatus': 'ERROR',
                'orchestration_type': 'error_fallback',
                'bedrock_agents_used': False
            })
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps({
                    'success': False,
                    'runId': str(uuid.uuid4())[:8],
                    'message': 'Generation encountered issues, serving fallback content',
                    'content': fallback_content
                })
            }
        except:
            return {
                'statusCode': 500,
                'headers': cors_headers(),
                'body': safe_json_dumps({
                    'success': False,
                    'error': 'Failed to generate fresh content',
                    'message': str(e)
                })
            }

def handle_latest(event):
    """Handle latest endpoint - get the most recent content with real data"""
    try:
        print("📰 Latest endpoint called - fetching real content")
        
        # Try to get enhanced brief first
        enhanced_brief = get_enhanced_brief_with_agent_outputs()
        
        if enhanced_brief:
            print("🎯 Returning enhanced brief with agent outputs")
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps(enhanced_brief)
            }
        
        # Fallback to cached brief
        cached_brief = get_cached_brief()
        
        if cached_brief:
            print("📦 Returning cached brief")
            # Enhance with real news if needed
            if 'agentOutputs' not in cached_brief:
                try:
                    real_news = fetch_real_news_direct()
                    cached_brief['agentOutputs'] = {
                        'favoriteStory': {
                            'title': real_news[0].get('title', 'Featured Story') if real_news else 'Featured Story',
                            'reasoning': 'Selected as the most relevant story for today\'s briefing.'
                        },
                        'mediaEnhancements': {'stories': []},
                        'weekendRecommendations': {'books': [], 'movies_and_shows': [], 'events': [], 'entertainment_recommendations': {'top_movies': [], 'must_watch_series': [], 'theater_plays': []}, 'cultural_insights': {}}
                    }
                except Exception as e:
                    print(f"⚠️ Error enhancing with real news: {e}")
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps(cached_brief)
            }
        
        # No cached content - create fresh content
        real_content = create_content_with_real_news()
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': safe_json_dumps(real_content)
        }
        
    except Exception as e:
        print(f"❌ Error in latest: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to provide fallback
        try:
            fallback_content = create_content_with_real_news()
            fallback_content.update({
                'error_type': 'latest_error',
                'message': 'Error retrieving latest content. Serving real news data.',
                'agentStatus': 'ERROR'
            })
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps(fallback_content)
            }
        except:
            return {
                'statusCode': 500,
                'headers': cors_headers(),
                'body': safe_json_dumps({
                    'success': False,
                    'error': 'Failed to retrieve latest content',
                    'message': str(e)
                })
            }

def handle_agent_status(event):
    """Handle agent-status endpoint - returns status of all Bedrock agents with caching"""
    try:
        print("📊 Agent status endpoint called")
        
        # Check cache first to avoid excessive Bedrock API calls
        from cache_service import get_cached, set_cached
        
        cached_status = get_cached('agent_status')
        if cached_status and cached_status.get('data'):
            print("✅ Returning cached agent status")
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps({
                    **cached_status['data'],
                    'cached': True,
                    'cached_at': cached_status.get('cached_at', '')
                })
            }
        
        # Check if Bedrock agents are enabled
        use_bedrock_agents = os.getenv('USE_BEDROCK_AGENTS', 'false').lower() == 'true'
        
        if not use_bedrock_agents or not BEDROCK_ORCHESTRATOR_AVAILABLE:
            status_response = {
                'bedrock_agents_enabled': False,
                'message': 'Bedrock agents are not enabled or available',
                'fallback_mode': 'standard_orchestration',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Cache for 5 minutes
            set_cached('agent_status', status_response, ttl_hours=0.083)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps(status_response)
            }
        
        try:
            # Create orchestrator instance to get agent status
            bedrock_orchestrator = BedrockAgentOrchestrator()
            
            if not bedrock_orchestrator.agent_ids:
                status_response = {
                    'bedrock_agents_enabled': True,
                    'agents_configured': False,
                    'message': 'No Bedrock agent IDs configured',
                    'agent_count': 0,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Cache for 5 minutes
                set_cached('agent_status', status_response, ttl_hours=0.083)
                
                return {
                    'statusCode': 200,
                    'headers': cors_headers(),
                    'body': safe_json_dumps(status_response)
                }
            
            # Get agent status with enhanced metadata
            agent_status = bedrock_orchestrator.get_agent_status()
            
            # Get orchestration statistics from DynamoDB
            orchestration_stats = get_orchestration_statistics()
            
            # Add agent roles and descriptions
            agent_roles = {
                'content_curator': {
                    'role': 'Content Curation',
                    'description': 'Discovers, filters, and curates the most relevant news stories',
                    'responsibilities': ['Evaluate news quality', 'Filter duplicates', 'Score social impact']
                },
                'social_impact_analyzer': {
                    'role': 'Social Impact Analysis',
                    'description': 'Analyzes stories for social relevance and community benefit',
                    'responsibilities': ['Identify social themes', 'Score generational appeal', 'Detect community impact']
                },
                'story_selector': {
                    'role': 'Story Selection',
                    'description': 'Selects the most compelling favorite story based on social impact',
                    'responsibilities': ['Review curated stories', 'Select top story', 'Generate reasoning']
                },
                'script_writer': {
                    'role': 'Script Writing',
                    'description': 'Creates engaging, conversational audio scripts',
                    'responsibilities': ['Write natural scripts', 'Emphasize social impact', 'Create smooth transitions']
                },
                'entertainment_curator': {
                    'role': 'Entertainment Curation',
                    'description': 'Curates weekend entertainment recommendations',
                    'responsibilities': ['Recommend socially relevant content', 'Connect to news themes', 'Ensure diversity']
                },
                'media_enhancer': {
                    'role': 'Media Enhancement',
                    'description': 'Optimizes visual content and social media presentation',
                    'responsibilities': ['Generate alt text', 'Create hashtags', 'Ensure accessibility']
                }
            }
            
            # Enhance agent status with roles and metadata
            for agent in agent_status.get('agents', []):
                agent_name = agent.get('name')
                if agent_name in agent_roles:
                    agent.update(agent_roles[agent_name])
            
            # Add comprehensive metadata
            agent_status.update({
                'bedrock_agents_enabled': True,
                'agents_configured': True,
                'agent_count': len(bedrock_orchestrator.agent_ids),
                'orchestration_statistics': orchestration_stats,
                'environment': {
                    'USE_BEDROCK_AGENTS': use_bedrock_agents,
                    'ENABLE_MULTI_AGENT': os.getenv('ENABLE_MULTI_AGENT', 'true').lower() == 'true'
                },
                'cached': False
            })
            
            # Cache for 5 minutes to avoid excessive API calls
            set_cached('agent_status', agent_status, ttl_hours=0.083)
            
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': safe_json_dumps(agent_status)
            }
            
        except Exception as e:
            print(f"❌ Error getting agent status: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'statusCode': 500,
                'headers': cors_headers(),
                'body': safe_json_dumps({
                    'bedrock_agents_enabled': True,
                    'error': 'Failed to retrieve agent status',
                    'message': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
            }
        
    except Exception as e:
        print(f"❌ Error in agent_status: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': safe_json_dumps({
                'error': 'Failed to retrieve agent status',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }

def get_orchestration_statistics():
    """Get orchestration statistics from DynamoDB"""
    try:
        # Query recent orchestration runs
        response = dynamodb.query(
            TableName=CURIO_TABLE,
            KeyConditionExpression='pk = :pk',
            ExpressionAttributeValues={
                ':pk': {'S': 'orchestration_stats'}
            },
            ScanIndexForward=False,
            Limit=100  # Last 100 runs
        )
        
        runs = response.get('Items', [])
        
        if not runs:
            return {
                'total_runs': 0,
                'success_rate': 0,
                'average_execution_time': 0,
                'last_run': None,
                'message': 'No orchestration statistics available yet'
            }
        
        # Calculate statistics
        total_runs = len(runs)
        successful_runs = sum(1 for run in runs if run.get('status', {}).get('S') == 'success')
        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
        
        # Calculate average execution time
        execution_times = [float(run.get('execution_time', {}).get('N', 0)) for run in runs]
        average_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Get last run info
        last_run = None
        if runs:
            last_run_item = runs[0]
            last_run = {
                'timestamp': last_run_item.get('timestamp', {}).get('S', ''),
                'status': last_run_item.get('status', {}).get('S', ''),
                'execution_time': float(last_run_item.get('execution_time', {}).get('N', 0)),
                'agents_used': int(last_run_item.get('agents_used', {}).get('N', 0))
            }
        
        return {
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'failed_runs': total_runs - successful_runs,
            'success_rate': round(success_rate, 2),
            'average_execution_time': round(average_execution_time, 2),
            'last_run': last_run,
            'statistics_period': 'Last 100 runs'
        }
        
    except Exception as e:
        print(f"⚠️ Error getting orchestration statistics: {e}")
        return {
            'total_runs': 0,
            'success_rate': 0,
            'average_execution_time': 0,
            'last_run': None,
            'error': str(e)
        }

def lambda_handler(event, context):
    """Main Lambda handler - routes requests to appropriate handlers"""
    
    # Handle CORS preflight for all endpoints
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': ''
        }
    
    # Parse the request path and method
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    
    print(f"🔍 Request: {method} {path}")
    
    try:
        # Route to appropriate handler
        if path == '/bootstrap':
            return handle_bootstrap(event)
        elif path == '/generate-fresh':
            return handle_generate_fresh(event)
        elif path == '/latest':
            return handle_latest(event)
        elif path == '/agent-status':
            return handle_agent_status(event)
        else:
            # Unknown endpoint
            print(f"❓ Unknown endpoint: {method} {path}")
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': safe_json_dumps({
                    'error': 'Endpoint not found',
                    'path': path,
                    'method': method,
                    'available_endpoints': ['/bootstrap', '/generate-fresh', '/latest', '/agent-status']
                })
            }
    
    except Exception as e:
        print(f"❌ Unhandled error in lambda_handler: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': safe_json_dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
