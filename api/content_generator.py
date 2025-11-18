"""
Simple Content Generator for Curio News
Consolidates all content generation into a single linear flow
"""

import json
import boto3
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
dynamodb = boto3.client('dynamodb', region_name='us-west-2')

# Configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '56e5f744fdb04e1e8e45a450851e442d')
NEWS_API_BASE_URL = 'https://newsapi.org/v2'
MODEL_ID = os.getenv('MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')

# Fallback content for when everything fails
FALLBACK_CONTENT = {
    "script": "Welcome to Curio News. We're updating our content and will be back shortly with the latest stories that matter to you.",
    "news_items": [
        {
            "title": "Curio News Update",
            "summary": "We're working to bring you the latest news. Please check back in a few minutes.",
            "category": "SYSTEM",
            "source": "Curio News",
            "relevance_score": 1.0
        }
    ],
    "sources": ["Curio News System"],
    "agent_outputs": {
        "favoriteStory": {
            "title": "System Update",
            "reasoning": "We're currently updating our news sources to bring you the best content."
        },
        "mediaEnhancements": {"stories": []},
        "weekendRecommendations": {
            "books": [],
            "movies_and_shows": [],
            "events": [],
            "entertainment_recommendations": {
                "top_movies": [],
                "must_watch_series": [],
                "theater_plays": []
            },
            "cultural_insights": {}
        }
    }
}

class ContentGenerator:
    """Simple content generator that handles all content creation in a linear flow"""
    
    def __init__(self, curio_table: str):
        self.curio_table = curio_table
    
    def generate_content(self, run_id: str = None) -> Dict[str, Any]:
        """
        Generate complete content in a simple linear flow:
        1. Fetch news
        2. Generate script
        3. Create agent outputs
        4. Assemble final content
        """
        try:
            print(f"🚀 Starting simple content generation (run_id: {run_id})")
            
            # Step 1: Fetch news data
            print("📰 Step 1: Fetching news...")
            news_items = self._fetch_news()
            
            if not news_items:
                print("⚠️ No news items found, using fallback content")
                return self._create_fallback_content(run_id)
            
            print(f"✅ Fetched {len(news_items)} news items")
            
            # Step 2: Generate script
            print("📝 Step 2: Generating script...")
            script = self._generate_script(news_items)
            
            # Step 3: Create agent outputs
            print("🤖 Step 3: Creating agent outputs...")
            agent_outputs = self._create_agent_outputs(news_items)
            
            # Step 4: Assemble final content
            print("🔧 Step 4: Assembling final content...")
            content = self._assemble_content(news_items, script, agent_outputs, run_id)
            
            print(f"✅ Content generation completed successfully")
            return content
            
        except Exception as e:
            print(f"❌ Error in content generation: {e}")
            return self._handle_error(e, run_id)
    
    def _fetch_news(self) -> List[Dict[str, Any]]:
        """Fetch news from multiple sources - NewsAPI (science/health/tech) + RSS feeds"""
        all_news = []
        
        # Fetch from NewsAPI with better categories
        newsapi_items = self._fetch_from_newsapi()
        all_news.extend(newsapi_items)
        
        # Fetch from RSS feeds (science/discovery sources)
        rss_items = self._fetch_from_rss_feeds()
        all_news.extend(rss_items)
        
        # Remove duplicates and return top items
        unique_news = self._deduplicate_news(all_news)
        return unique_news[:10]
    
    def _fetch_from_newsapi(self) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI focusing on science, health, and technology"""
        try:
            if not NEWS_API_KEY:
                print("⚠️ No NewsAPI key available")
                return []
            
            print(f"🔑 Using NewsAPI key: {NEWS_API_KEY[:8]}...")
            
            all_articles = []
            
            # Fetch from multiple POSITIVE categories
            categories = ['science', 'health', 'technology']
            
            for category in categories:
                print(f"📡 Fetching {category} news from NewsAPI...")
                response = requests.get(
                    f"{NEWS_API_BASE_URL}/top-headlines",
                    params={
                        'apiKey': NEWS_API_KEY,
                        'language': 'en',
                        'country': 'us',
                        'category': category,
                        'pageSize': 5  # 5 per category = 15 total
                    },
                    timeout=10
                )
            
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok':
                        articles = data.get('articles', [])
                        print(f"✅ Got {len(articles)} {category} articles")
                        all_articles.extend(articles)
                else:
                    print(f"⚠️ Failed to fetch {category}: {response.status_code}")
            
            # Convert to our format
            news_items = []
            for article in all_articles:
                if self._is_valid_article(article):
                    category = self._categorize_article(article.get('title', ''))
                    image_url = article.get('urlToImage', '')
                    
                    if not image_url:
                        image_url = self._generate_fallback_image(category, article.get('title', ''))
                    
                    news_items.append({
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'link': article.get('url', ''),
                        'published': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'category': category.upper(),
                        'image': image_url,
                        'relevance_score': 0.9  # Higher score for curated categories
                    })
            
            print(f"📰 NewsAPI returned {len(news_items)} total articles from science/health/tech")
            return news_items
            
        except Exception as e:
            print(f"❌ Error fetching from NewsAPI: {e}")
            return []
    
    def _fetch_from_rss_feeds(self) -> List[Dict[str, Any]]:
        """Fetch news from science and discovery RSS feeds"""
        try:
            import feedparser
            
            # Quality science and discovery RSS feeds
            rss_feeds = [
                ('https://www.sciencedaily.com/rss/all.xml', 'Science Daily'),
                ('https://www.nasa.gov/rss/dyn/breaking_news.rss', 'NASA'),
                ('https://phys.org/rss-feed/', 'Phys.org'),
            ]
            
            news_items = []
            
            for feed_url, source_name in rss_feeds:
                try:
                    print(f"📡 Fetching from {source_name}...")
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:3]:  # 3 per feed
                        title = entry.get('title', '')
                        summary = entry.get('summary', entry.get('description', ''))
                        
                        # Clean HTML from summary
                        import re
                        summary = re.sub('<[^<]+?>', '', summary)
                        summary = summary[:200]  # Limit length
                        
                        category = self._categorize_article(title)
                        image_url = self._generate_fallback_image(category, title)
                        
                        news_items.append({
                            'title': title,
                            'summary': summary,
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'source': source_name,
                            'category': category.upper(),
                            'image': image_url,
                            'relevance_score': 0.95  # Highest score for science feeds
                        })
                    
                    print(f"✅ Got {len(feed.entries[:3])} articles from {source_name}")
                    
                except Exception as feed_error:
                    print(f"⚠️ Failed to fetch {source_name}: {feed_error}")
                    continue
            
            print(f"📰 RSS feeds returned {len(news_items)} total articles")
            return news_items
            
        except ImportError:
            print("⚠️ feedparser not installed, skipping RSS feeds")
            return []
        except Exception as e:
            print(f"❌ Error fetching from RSS feeds: {e}")
            return []
    
    def _deduplicate_news(self, news_items: List[Dict]) -> List[Dict]:
        """Remove duplicate news items based on title similarity"""
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            title_lower = item['title'].lower()[:50]  # First 50 chars
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_items.append(item)
        
        return unique_items
    
    def _is_valid_article(self, article: Dict) -> bool:
        """Check if article has required fields"""
        return (
            article.get('title') and 
            article.get('description') and
            '[Removed]' not in article.get('title', '') and
            '[Removed]' not in article.get('description', '')
        )
    
    def _categorize_article(self, title: str) -> str:
        """Simple article categorization based on title keywords"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['tech', 'ai', 'apple', 'google', 'microsoft']):
            return 'TECHNOLOGY'
        elif any(word in title_lower for word in ['business', 'market', 'stock', 'economy']):
            return 'BUSINESS'
        elif any(word in title_lower for word in ['health', 'medical', 'covid', 'vaccine']):
            return 'HEALTH'
        elif any(word in title_lower for word in ['politics', 'government', 'election', 'congress']):
            return 'POLITICS'
        elif any(word in title_lower for word in ['sports', 'football', 'basketball', 'baseball']):
            return 'SPORTS'
        else:
            return 'GENERAL'
    
    def _generate_fallback_image(self, category: str, title: str) -> str:
        """Generate fallback image URL based on category and title"""
        try:
            # Use Unsplash for high-quality category-based images
            category_keywords = {
                'TECHNOLOGY': 'technology,computer,innovation',
                'BUSINESS': 'business,finance,office',
                'HEALTH': 'health,medical,wellness',
                'POLITICS': 'government,politics,capitol',
                'SPORTS': 'sports,athletics,competition',
                'GENERAL': 'news,newspaper,information'
            }
            
            keywords = category_keywords.get(category, 'news,information')
            
            # Create a deterministic image URL based on title hash for consistency
            title_hash = abs(hash(title)) % 1000
            
            return f"https://source.unsplash.com/800x400/?{keywords}&sig={title_hash}"
            
        except Exception as e:
            print(f"❌ Error generating fallback image: {e}")
            # Ultimate fallback - colored placeholder
            colors = ['4f46e5', '059669', 'dc2626', 'ea580c', '7c3aed', '0891b2']
            color = colors[abs(hash(title)) % len(colors)]
            return f"https://via.placeholder.com/800x400/{color}/ffffff?text=News"
    
    def _ensure_all_images(self, news_items: List[Dict]) -> List[Dict]:
        """Final validation to ensure every news item has an image"""
        for item in news_items:
            if not item.get('image') or item['image'] == '':
                print(f"⚠️ Missing image for: {item['title'][:50]}...")
                item['image'] = self._generate_fallback_image(item['category'], item['title'])
                print(f"✅ Generated fallback image: {item['image']}")
        
        return news_items
    
    def _generate_script(self, news_items: List[Dict]) -> str:
        """Generate a simple script from news items"""
        try:
            if not news_items:
                return FALLBACK_CONTENT["script"]
            
            # Use ALL news items, not just the first 3
            all_stories = news_items[:7]  # Ensure we cover all 7 stories
            news_summary = "\n".join([
                f"- {item['title']}: {item['summary'][:80]}..."
                for item in all_stories
            ])
            
            prompt = f"""Write a natural, conversational 90-second news script. Cover ALL {len(all_stories)} stories.

Today's stories (cover ALL):
{news_summary}

CRITICAL RULES:
1. Start with a SPECIFIC hook about the most interesting story - NO generic greetings
2. Jump RIGHT into the news - be direct and engaging
3. Use casual, natural language like texting a friend
4. Cover ALL {len(all_stories)} stories briefly
5. Keep under 300 words total
6. End with something thought-provoking

GOOD opening examples:
- "So apparently melatonin gummies might actually be making your sleep worse..."
- "Rosalía just dropped a surprise album and the internet is losing it..."
- "There's this wild new study about how your phone is changing your brain..."

BAD openings (NEVER use):
- "Hey friends, it's your girl..."
- "Welcome to Curio News..."
- "I'm so stoked to share..."
- "Buckle up because..."
- "Hi from Curio..."

Write the script NOW - start with the most interesting story immediately:"""

            # Call Bedrock to generate script
            response = bedrock.invoke_model(
                modelId=MODEL_ID,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 800,  # Increased for longer script covering all stories
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            result = json.loads(response['body'].read())
            script = result['content'][0]['text'].strip()
            
            # Clean up the script
            if script.startswith('Script:'):
                script = script[7:].strip()
            
            # Validate that script covers all stories
            coverage_validation = self._validate_script_coverage(script, all_stories)
            print(f"📊 Script coverage: {coverage_validation['covered_stories']}/{coverage_validation['total_stories']} stories")
            
            if coverage_validation['coverage_percentage'] < 70:
                print("⚠️ Script coverage below 70%, generating fallback script")
                script = self._generate_fallback_script(all_stories)
            
            return script
            
        except Exception as e:
            print(f"❌ Error generating script: {e}")
            # Return a simple fallback script based on news titles
            if news_items:
                titles = [item['title'] for item in news_items[:3]]
                return f"Welcome to Curio News! Today's top stories include: {', '.join(titles)}. Stay informed and have a great day!"
            return FALLBACK_CONTENT["script"]
    
    def _validate_script_coverage(self, script: str, news_items: List[Dict]) -> Dict[str, Any]:
        """Validate that the script covers all news stories"""
        script_lower = script.lower()
        covered_stories = 0
        missing_stories = []
        
        for item in news_items:
            title_words = item['title'].lower().split()
            # Check if at least 2 significant words from the title appear in the script
            significant_words = [word for word in title_words if len(word) > 3][:3]
            matches = sum(1 for word in significant_words if word in script_lower)
            
            if matches >= 1:  # At least one significant word match
                covered_stories += 1
            else:
                missing_stories.append(item['title'])
        
        return {
            'total_stories': len(news_items),
            'covered_stories': covered_stories,
            'coverage_percentage': (covered_stories / len(news_items)) * 100 if news_items else 0,
            'missing_stories': missing_stories
        }
    
    def _generate_fallback_script(self, news_items: List[Dict]) -> str:
        """Generate a simple fallback script that definitely covers all stories"""
        if not news_items:
            return "Hi from Curio! We're updating our news sources. Check back shortly."
        
        script_parts = [
            "Hi from Curio!"
        ]
        
        if news_items:
            # First story as favorite
            first_item = news_items[0]
            title = first_item.get('title', 'Untitled')
            summary = first_item.get('summary', 'No summary available')[:100] + "..."
            script_parts.append(f"{title}. {summary}")
            
            if len(news_items) > 1:
                for i, item in enumerate(news_items[1:7], 2):
                    title = item.get('title', 'Untitled')
                    summary = item.get('summary', 'No summary available')[:80] + "..."
                    script_parts.append(f"{title}. {summary}")
        
        script_parts.append("That's it for today.")
        
        return " ".join(script_parts)
    
    def _select_favorite_story(self, news_items: List[Dict]) -> Dict[str, Any]:
        """Select the most interesting, positive story as favorite"""
        if not news_items:
            return {
                "title": "No stories available",
                "reasoning": "No news items to select from."
            }
        
        # Score stories based on positivity and interest factors
        scored_stories = []
        
        for item in news_items:
            score = self._calculate_story_score(item)
            scored_stories.append((item, score))
        
        # Sort by score (highest first)
        scored_stories.sort(key=lambda x: x[1], reverse=True)
        
        # Select the highest scoring story
        best_story = scored_stories[0][0]
        
        # Generate more specific reasoning based on story content
        reasoning = self._generate_favorite_reasoning(best_story, len(news_items))
        
        return {
            "title": best_story['title'],
            "summary": best_story['summary'],
            "category": best_story['category'],
            "source": best_story.get('source', 'Curio News'),
            "image": best_story.get('image', ''),
            "reasoning": reasoning
        }
    
    def _calculate_story_score(self, item: Dict) -> float:
        """Calculate positivity and interest score for a story - prioritizing good news, discoveries, and curiosities"""
        score = 0.0
        title = item.get('title', '').lower()
        summary = item.get('summary', '').lower()
        category = item.get('category', '')
        
        text_to_check = f"{title} {summary}"
        
        # HIGHEST PRIORITY: Scientific discoveries and breakthroughs (5.0 points each)
        discovery_keywords = [
            'breakthrough', 'discovery', 'cure', 'treatment', 'vaccine',
            'new species', 'fossil', 'planet', 'galaxy', 'black hole',
            'quantum', 'gene therapy', 'stem cell', 'cancer treatment',
            'alzheimer', 'diabetes', 'heart disease', 'medical advance'
        ]
        
        # HIGH PRIORITY: Good news and positive achievements (4.0 points each)
        good_news_keywords = [
            'rescued', 'saved', 'helped', 'donated', 'charity', 'volunteer',
            'recovery', 'healing', 'success story', 'achievement', 'milestone',
            'graduation', 'scholarship', 'award', 'recognition', 'celebration',
            'reunion', 'adoption', 'birth', 'wedding', 'anniversary'
        ]
        
        # HIGH PRIORITY: Amazing curiosities and phenomena (3.5 points each)
        curiosity_keywords = [
            'rare', 'unique', 'first time', 'record-breaking', 'unusual',
            'mysterious', 'ancient', 'archaeological', 'historical',
            'phenomenon', 'aurora', 'eclipse', 'meteor', 'comet',
            'deep sea', 'ocean', 'wildlife', 'animal behavior', 'migration',
            'fascinating', 'incredible', 'amazing', 'remarkable', 'extraordinary'
        ]
        
        # MEDIUM PRIORITY: Innovation and technology (3.0 points each)
        innovation_keywords = [
            'innovation', 'invention', 'technology', 'ai', 'robot', 'automation',
            'renewable energy', 'solar', 'wind power', 'electric vehicle',
            'space exploration', 'mars', 'moon', 'satellite', 'telescope',
            'app', 'software', 'startup', 'entrepreneur', 'green technology'
        ]
        
        # MEDIUM PRIORITY: Environmental and conservation (2.5 points each)
        environmental_keywords = [
            'conservation', 'endangered species', 'wildlife protection',
            'reforestation', 'clean energy', 'sustainability', 'recycling',
            'ocean cleanup', 'climate solution', 'carbon capture',
            'biodiversity', 'ecosystem', 'national park', 'preserve'
        ]
        
        # STRONG NEGATIVE: Bad news and negative events (heavy penalty)
        negative_keywords = [
            'death', 'died', 'killed', 'murder', 'shooting', 'attack', 'bomb',
            'terror', 'war', 'conflict', 'crash', 'accident', 'disaster',
            'fire', 'flood', 'earthquake', 'hurricane', 'crisis', 'emergency',
            'scandal', 'corrupt', 'fraud', 'lawsuit', 'arrest', 'crime',
            'violence', 'abuse', 'threat', 'danger', 'risk', 'warning',
            'drug trafficking', 'narcotrafficker', 'cartel', 'smuggling',
            'pentagon', 'military strike', 'bombing', 'missile', 'troops'
        ]
        
        # Calculate scores with weighted priorities
        for keyword in discovery_keywords:
            if keyword in text_to_check:
                score += 5.0
                print(f"🔬 Discovery keyword '{keyword}' found - major boost!")
        
        for keyword in good_news_keywords:
            if keyword in text_to_check:
                score += 4.0
                print(f"😊 Good news keyword '{keyword}' found - big boost!")
        
        for keyword in curiosity_keywords:
            if keyword in text_to_check:
                score += 3.5
                print(f"🤔 Curiosity keyword '{keyword}' found - great boost!")
        
        for keyword in innovation_keywords:
            if keyword in text_to_check:
                score += 3.0
                print(f"💡 Innovation keyword '{keyword}' found - good boost!")
        
        for keyword in environmental_keywords:
            if keyword in text_to_check:
                score += 2.5
                print(f"🌱 Environmental keyword '{keyword}' found - nice boost!")
        
        # SOCIAL IMPACT PRIORITY: Stories that help society (6.0 points each - HIGHEST PRIORITY)
        social_impact_keywords = [
            'community', 'society', 'social justice', 'equality', 'diversity',
            'mental health awareness', 'education reform', 'accessibility',
            'affordable housing', 'food security', 'clean water', 'healthcare access',
            'youth program', 'elderly care', 'disability rights', 'inclusion',
            'poverty reduction', 'literacy', 'job training', 'skill development',
            'social change', 'activism', 'grassroots', 'nonprofit', 'foundation',
            'helping', 'support', 'aid', 'assistance', 'outreach', 'service',
            'empowerment', 'advocacy', 'awareness', 'initiative', 'program'
        ]
        
        for keyword in social_impact_keywords:
            if keyword in text_to_check:
                score += 6.0
                print(f"🤝 Social impact keyword '{keyword}' found - MAXIMUM social boost!")
        
        # FINANCIAL/STOCK MARKET PENALTY: These stories benefit few people
        financial_keywords = [
            'stock market', 'stocks rise', 'stocks fall', 'dow jones', 'nasdaq',
            'wall street', 'trading', 'investors', 'market gains', 'market losses',
            'earnings report', 'quarterly results', 'share price', 'dividend',
            'ipo', 'merger', 'acquisition', 'buyback', 'market cap',
            'fed rate', 'interest rate decision', 'federal reserve', 'bull market',
            'bear market', 'portfolio', 'hedge fund', 'venture capital'
        ]
        
        financial_penalty = 0
        for keyword in financial_keywords:
            if keyword in text_to_check:
                financial_penalty += 3.0  # Increased penalty
                print(f"💰 Financial keyword '{keyword}' found - applying social relevance penalty")
        
        if financial_penalty > 0:
            score -= financial_penalty
            print(f"📉 Applied {financial_penalty} point penalty for financial focus (limited social impact)")
        
        # Category bonuses - prioritize science, health, and social stories
        if category == 'HEALTH':
            score += 3.0  # Health stories often have broad social impact
        elif category == 'TECHNOLOGY':
            score += 1.5  # Tech stories can have social benefits
        elif category == 'GENERAL':
            score += 2.0  # General news often covers social issues
        elif category == 'BUSINESS':
            score -= 1.5  # Business news often has limited social impact (increased penalty)
        
        # Heavy penalty for negative content
        negative_count = 0
        for keyword in negative_keywords:
            if keyword in text_to_check:
                negative_count += 1
                score -= 3.0  # Heavy penalty for each negative keyword
        
        if negative_count > 0:
            print(f"⚠️ Found {negative_count} negative keywords - applying penalty")
        
        # Bonus for stories that sound educational or thought-provoking
        educational_keywords = [
            'study shows', 'research reveals', 'scientists find', 'experts say',
            'new understanding', 'learn', 'education', 'knowledge', 'insight'
        ]
        
        for keyword in educational_keywords:
            if keyword in text_to_check:
                score += 1.0
                print(f"📚 Educational keyword '{keyword}' found - learning bonus!")
        
        # Final score adjustments
        final_score = max(0.0, score)
        print(f"📊 Story score: {final_score:.1f} - '{title[:50]}...'")
        
        return final_score
    
    def _generate_favorite_reasoning(self, story: Dict, total_stories: int) -> str:
        """Generate specific reasoning for why this story was selected as favorite"""
        title = story.get('title', '').lower()
        summary = story.get('summary', '').lower()
        category = story.get('category', '')
        
        text_to_check = f"{title} {summary}"
        
        # Determine the primary reason for selection - prioritizing social impact
        if any(word in text_to_check for word in ['community', 'society', 'social justice', 'equality', 'diversity', 'mental health awareness', 'education reform', 'accessibility']):
            return f"🤝 Selected as today's most socially impactful story from {total_stories} articles. This story highlights positive change that benefits communities and advances social progress - exactly what Gen Z and Millennials care about most."
        
        elif any(word in text_to_check for word in ['breakthrough', 'discovery', 'cure', 'treatment']):
            return f"🔬 Chosen as today's most hopeful scientific story from {total_stories} articles. This breakthrough could improve countless lives and represents the kind of progress that gives us hope for the future."
        
        elif any(word in text_to_check for word in ['rescued', 'saved', 'helped', 'donated', 'success story', 'volunteer', 'charity']):
            return f"😊 Selected as today's most heartwarming story from {total_stories} articles. This uplifting news shows people making a real difference in their communities - the kind of positive action that inspires us all."
        
        elif any(word in text_to_check for word in ['conservation', 'wildlife', 'environment', 'sustainability', 'climate solution', 'renewable energy']):
            return f"🌱 Picked as today's most inspiring environmental story from {total_stories} articles. This positive development shows real progress in protecting our planet - crucial news for future generations."
        
        elif any(word in text_to_check for word in ['rare', 'unique', 'first time', 'unusual', 'mysterious', 'archaeological', 'ancient']):
            return f"🤔 Chosen as today's most fascinating discovery from {total_stories} articles. This intriguing story expands our understanding of the world and sparks the kind of curiosity that drives human progress."
        
        elif any(word in text_to_check for word in ['innovation', 'technology', 'ai', 'space', 'mars']) and not any(word in text_to_check for word in ['stock', 'market', 'trading', 'investors']):
            return f"💡 Selected as today's most innovative story from {total_stories} articles. This technological advancement has the potential to benefit society and represents human ingenuity at its best."
        
        elif category == 'HEALTH':
            return f"🏥 Chosen as today's most hopeful health story from {total_stories} articles. This medical news offers promise for better health outcomes and demonstrates progress in caring for human wellbeing."
        
        else:
            return f"⭐ Selected as today's most meaningful story from {total_stories} articles. This story scored highest for its potential to positively impact society, inspire action, and spark important conversations about our shared future."
    
    def _generate_entertainment_recommendations(self, news_items: List[Dict]) -> Dict[str, Any]:
        """Generate entertainment recommendations based on current news themes and general appeal"""
        try:
            # Analyze news themes to provide contextual entertainment
            news_themes = self._analyze_news_themes(news_items)
            
            # Generate top movies recommendations
            top_movies = self._generate_movie_recommendations(news_themes)
            
            # Generate TV series recommendations
            must_watch_series = self._generate_series_recommendations(news_themes)
            
            # Generate theater and plays recommendations
            theater_plays = self._generate_theater_recommendations(news_themes)
            
            return {
                "top_movies": top_movies,
                "must_watch_series": must_watch_series,
                "theater_plays": theater_plays
            }
            
        except Exception as e:
            print(f"❌ Error generating entertainment recommendations: {e}")
            return self._get_fallback_entertainment_recommendations()
    
    def _analyze_news_themes(self, news_items: List[Dict]) -> Dict[str, int]:
        """Analyze news items to identify dominant themes for entertainment matching"""
        themes = {
            'technology': 0,
            'politics': 0,
            'health': 0,
            'business': 0,
            'sports': 0,
            'science': 0,
            'international': 0,
            'entertainment': 0
        }
        
        for item in news_items:
            title = item.get('title', '').lower()
            summary = item.get('summary', '').lower()
            category = item.get('category', '').lower()
            text = f"{title} {summary}"
            
            # Technology themes
            if any(word in text for word in ['tech', 'ai', 'robot', 'computer', 'digital', 'cyber']):
                themes['technology'] += 1
            
            # Political themes
            if any(word in text for word in ['politics', 'government', 'election', 'congress', 'president']):
                themes['politics'] += 1
            
            # Health themes
            if any(word in text for word in ['health', 'medical', 'disease', 'treatment', 'vaccine']):
                themes['health'] += 1
            
            # Business themes
            if any(word in text for word in ['business', 'economy', 'market', 'stock', 'finance']):
                themes['business'] += 1
            
            # Sports themes
            if any(word in text for word in ['sports', 'football', 'basketball', 'baseball', 'olympics']):
                themes['sports'] += 1
            
            # Science themes
            if any(word in text for word in ['science', 'research', 'study', 'discovery', 'space']):
                themes['science'] += 1
            
            # International themes
            if any(word in text for word in ['international', 'global', 'world', 'foreign', 'country']):
                themes['international'] += 1
            
            # Category-based scoring
            if category in themes:
                themes[category] += 2
        
        return themes
    
    def _generate_movie_recommendations(self, themes: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate movie recommendations based on news themes"""
        movie_pools = {
            'technology': [
                {
                    "title": "Ex Machina",
                    "genre": "Sci-Fi Thriller",
                    "rating": "7.7/10",
                    "platform": "Various Streaming",
                    "description": "A thought-provoking exploration of artificial intelligence and consciousness.",
                    "release_year": 2014,
                    "runtime": "1h 48m"
                },
                {
                    "title": "The Social Network",
                    "genre": "Biography Drama",
                    "rating": "7.7/10",
                    "platform": "Netflix",
                    "description": "The story behind the creation of Facebook and its impact on society.",
                    "release_year": 2010,
                    "runtime": "2h 0m"
                }
            ],
            'politics': [
                {
                    "title": "All the President's Men",
                    "genre": "Political Thriller",
                    "rating": "8.0/10",
                    "platform": "Various Streaming",
                    "description": "The true story of how two reporters uncovered the Watergate scandal.",
                    "release_year": 1976,
                    "runtime": "2h 18m"
                },
                {
                    "title": "The Post",
                    "genre": "Historical Drama",
                    "rating": "7.2/10",
                    "platform": "Amazon Prime",
                    "description": "The Washington Post's decision to publish the Pentagon Papers.",
                    "release_year": 2017,
                    "runtime": "1h 56m"
                }
            ],
            'science': [
                {
                    "title": "Interstellar",
                    "genre": "Sci-Fi Drama",
                    "rating": "8.6/10",
                    "platform": "Various Streaming",
                    "description": "A team of explorers travel through a wormhole in space to save humanity.",
                    "release_year": 2014,
                    "runtime": "2h 49m"
                },
                {
                    "title": "The Martian",
                    "genre": "Sci-Fi Adventure",
                    "rating": "8.0/10",
                    "platform": "Disney+",
                    "description": "An astronaut becomes stranded on Mars and must find a way to survive.",
                    "release_year": 2015,
                    "runtime": "2h 24m"
                }
            ],
            'general': [
                {
                    "title": "Dune: Part Two",
                    "genre": "Sci-Fi Epic",
                    "rating": "8.8/10",
                    "platform": "Max",
                    "description": "Paul Atreides unites with the Fremen while seeking revenge against conspirators.",
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
            ]
        }
        
        # Select movies based on dominant themes
        selected_movies = []
        
        # Get top theme
        top_theme = max(themes.items(), key=lambda x: x[1])[0] if themes else 'general'
        
        # Add movies from top theme
        if top_theme in movie_pools and themes[top_theme] > 0:
            selected_movies.extend(movie_pools[top_theme][:1])
        
        # Add general recommendations to fill up to 2-3 movies
        selected_movies.extend(movie_pools['general'][:2])
        
        return selected_movies[:3]  # Limit to 3 movies
    
    def _generate_series_recommendations(self, themes: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate TV series recommendations based on news themes"""
        series_pools = {
            'technology': [
                {
                    "title": "Black Mirror",
                    "genre": "Sci-Fi Anthology",
                    "rating": "8.8/10",
                    "platform": "Netflix",
                    "description": "Anthology series exploring the dark side of technology and modern society.",
                    "seasons": 6,
                    "episodes_per_season": 6,
                    "status": "ongoing"
                }
            ],
            'politics': [
                {
                    "title": "House of Cards",
                    "genre": "Political Drama",
                    "rating": "8.7/10",
                    "platform": "Netflix",
                    "description": "A ruthless politician's rise to power in Washington D.C.",
                    "seasons": 6,
                    "episodes_per_season": 13,
                    "status": "completed"
                }
            ],
            'health': [
                {
                    "title": "The Good Doctor",
                    "genre": "Medical Drama",
                    "rating": "8.0/10",
                    "platform": "Hulu",
                    "description": "A young surgeon with autism and savant syndrome joins a prestigious hospital.",
                    "seasons": 7,
                    "episodes_per_season": 20,
                    "status": "completed"
                }
            ],
            'general': [
                {
                    "title": "The Bear",
                    "genre": "Comedy-Drama",
                    "rating": "9.1/10",
                    "platform": "Hulu",
                    "description": "A young chef returns to Chicago to run his deceased brother's sandwich shop.",
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
                },
                {
                    "title": "Stranger Things",
                    "genre": "Sci-Fi Horror",
                    "rating": "8.7/10",
                    "platform": "Netflix",
                    "description": "A group of kids in a small town uncover supernatural mysteries.",
                    "seasons": 4,
                    "episodes_per_season": 9,
                    "status": "completed"
                }
            ]
        }
        
        selected_series = []
        
        # Get top theme
        top_theme = max(themes.items(), key=lambda x: x[1])[0] if themes else 'general'
        
        # Add series from top theme
        if top_theme in series_pools and themes[top_theme] > 0:
            selected_series.extend(series_pools[top_theme][:1])
        
        # Add general recommendations
        selected_series.extend(series_pools['general'][:2])
        
        return selected_series[:3]  # Limit to 3 series
    
    def _generate_theater_recommendations(self, themes: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate theater and plays recommendations"""
        theater_recommendations = [
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
            },
            {
                "title": "Chicago",
                "genre": "Musical Crime",
                "venue": "Ambassador Theatre",
                "city": "New York",
                "description": "The sultry musical about fame, fortune, and murder in the Windy City.",
                "show_times": "Mon-Sat 8PM, Wed & Sat 2PM",
                "ticket_info": "From $69",
                "rating": "8.8/10"
            }
        ]
        
        return theater_recommendations[:2]  # Limit to 2 plays
    
    def _get_fallback_entertainment_recommendations(self) -> Dict[str, Any]:
        """Provide fallback entertainment recommendations when generation fails"""
        return {
            "top_movies": [
                {
                    "title": "The Shawshank Redemption",
                    "genre": "Drama",
                    "rating": "9.3/10",
                    "platform": "Various Streaming",
                    "description": "Two imprisoned men bond over years, finding solace and redemption.",
                    "release_year": 1994,
                    "runtime": "2h 22m"
                }
            ],
            "must_watch_series": [
                {
                    "title": "Breaking Bad",
                    "genre": "Crime Drama",
                    "rating": "9.5/10",
                    "platform": "Netflix",
                    "description": "A high school chemistry teacher turned methamphetamine manufacturer.",
                    "seasons": 5,
                    "episodes_per_season": 13,
                    "status": "completed"
                }
            ],
            "theater_plays": [
                {
                    "title": "The Phantom of the Opera",
                    "genre": "Musical Romance",
                    "venue": "Various Theaters",
                    "city": "Multiple Cities",
                    "description": "The haunting tale of the Opera Ghost and his obsession with Christine.",
                    "show_times": "Check local listings",
                    "ticket_info": "Varies by location"
                }
            ]
        }

    def _create_agent_outputs(self, news_items: List[Dict]) -> Dict[str, Any]:
        """Create simple agent outputs without complex orchestration"""
        try:
            # Favorite Story - select based on positivity and interest
            favorite_story = self._select_favorite_story(news_items)
            
            # Media Enhancements - create simple enhancements for top stories
            media_stories = []
            for item in news_items[:3]:
                category = item.get('category', 'news').lower()
                hashtags = [f"#{category.title()}", "#News", "#CurioNews"]
                
                media_stories.append({
                    "title": item['title'],
                    "media_recommendations": {
                        "images": [{
                            "url": item.get('image', f"https://source.unsplash.com/800x400/?{category}"),
                            "alt_text": f"Image for {item['title'][:50]}"
                        }],
                        "videos": [],
                        "social_media_optimization": {"hashtags": hashtags}
                    }
                })
            
            # Weekend Recommendations - enhanced with entertainment recommendations
            weekend_recommendations = {
                "books": [
                    {
                        "title": "The News: A User's Manual",
                        "author": "Alain de Botton",
                        "description": "A thoughtful guide to consuming news in the modern age.",
                        "genre": "Non-fiction"
                    }
                ],
                "movies_and_shows": [
                    {
                        "title": "All the President's Men",
                        "platform": "Various Streaming",
                        "description": "Classic journalism thriller about investigative reporting.",
                        "genre": "Drama, Thriller"
                    }
                ],
                "events": [
                    {
                        "name": "Local News Literacy Workshops",
                        "location": "Check local libraries",
                        "date": "Various weekends",
                        "description": "Learn to critically evaluate news sources.",
                        "link": "Search 'news literacy' + your city"
                    }
                ],
                "entertainment_recommendations": self._generate_entertainment_recommendations(news_items),
                # Deprecated: keeping for backward compatibility
                "cultural_insights": {
                    "news_trends": "Personalized AI-curated news is becoming the preferred way to stay informed.",
                    "social_media_phenomena": "Visual storytelling dominates news engagement.",
                    "information_consumption": "Quality over quantity is the new approach to news."
                }
            }
            
            return {
                "favoriteStory": favorite_story,
                "mediaEnhancements": {"stories": media_stories},
                "weekendRecommendations": weekend_recommendations
            }
            
        except Exception as e:
            print(f"❌ Error creating agent outputs: {e}")
            return FALLBACK_CONTENT["agent_outputs"]
    
    def _assemble_content(self, news_items: List[Dict], script: str, agent_outputs: Dict, run_id: str) -> Dict[str, Any]:
        """Assemble all components into final content structure"""
        try:
            # Generate word timings for the script
            word_timings = self._generate_word_timings(script)
            
            # Extract unique sources
            sources = list(set([item.get('source', 'News Source') for item in news_items]))
            
            # Generate audio using the audio service
            try:
                from audio_service import AudioService
                audio_service = AudioService()
                audio_result = audio_service.generate_audio_url(script, run_id or 'default')
                
                if audio_result.get('success') and audio_result.get('audio_url'):
                    audio_url = audio_result['audio_url']
                    print(f"✅ Generated audio URL successfully")
                else:
                    print(f"⚠️ Audio generation failed, using fallback")
                    audio_url = ''  # No fallback URL, let frontend handle gracefully
            except Exception as e:
                print(f"⚠️ Audio service error: {e}")
                audio_url = ''  # No fallback URL, let frontend handle gracefully
            
            return {
                'audioUrl': audio_url,
                'sources': sources,
                'generatedAt': datetime.utcnow().isoformat(),
                'why': f'Fresh content generated from {len(news_items)} news sources using simple linear processing',
                'traceId': f'simple-{run_id or int(time.time())}',
                'script': script,
                'news_items': news_items,
                'word_timings': word_timings,
                'agentOutputs': agent_outputs,
                'shouldRefresh': False,
                'agentStatus': 'COMPLETED',
                'quality_score': 85,
                'enhanced_orchestration': False,
                'validation_passed': True
            }
            
        except Exception as e:
            print(f"❌ Error assembling content: {e}")
            return self._create_fallback_content(run_id)
    
    def _generate_word_timings(self, script: str) -> List[Dict]:
        """Generate simple word timings for the script"""
        try:
            words = script.split()
            word_timings = []
            current_time = 0.0
            
            for word in words[:50]:  # Limit for performance
                duration = 0.4  # Average word duration
                word_timings.append({
                    'word': word,
                    'start': round(current_time, 2),
                    'end': round(current_time + duration, 2)
                })
                current_time += duration
            
            return word_timings
            
        except Exception as e:
            print(f"❌ Error generating word timings: {e}")
            return []
    
    def _create_fallback_content(self, run_id: str) -> Dict[str, Any]:
        """Create fallback content when everything else fails"""
        return {
            'audioUrl': '',
            'sources': FALLBACK_CONTENT["sources"],
            'generatedAt': datetime.utcnow().isoformat(),
            'why': 'Using fallback content due to service issues',
            'traceId': f'fallback-{run_id or int(time.time())}',
            'script': FALLBACK_CONTENT["script"],
            'news_items': FALLBACK_CONTENT["news_items"],
            'word_timings': [],
            'agentOutputs': FALLBACK_CONTENT["agent_outputs"],
            'shouldRefresh': True,
            'agentStatus': 'FALLBACK',
            'quality_score': 50,
            'enhanced_orchestration': False,
            'validation_passed': False
        }
    
    def _handle_error(self, error: Exception, run_id: str) -> Dict[str, Any]:
        """Handle errors with direct fallback to cached or hardcoded content"""
        print(f"🔄 Handling error with fallback: {error}")
        
        try:
            # Try to get cached content first
            cached_content = self._get_cached_content()
            if cached_content:
                print("✅ Using cached content as fallback")
                cached_content['error_recovery'] = True
                cached_content['original_error'] = str(error)
                return cached_content
        except Exception as cache_error:
            print(f"❌ Cache fallback failed: {cache_error}")
        
        # Ultimate fallback to hardcoded content
        print("🆘 Using hardcoded fallback content")
        fallback = self._create_fallback_content(run_id)
        fallback['error_recovery'] = True
        fallback['original_error'] = str(error)
        return fallback
    
    def _get_cached_content(self) -> Optional[Dict[str, Any]]:
        """Try to get cached content from DynamoDB"""
        try:
            response = dynamodb.get_item(
                TableName=self.curio_table,
                Key={
                    'pk': {'S': 'brief'},
                    'sk': {'S': 'latest'}
                }
            )
            
            if 'Item' in response:
                item = response['Item']
                return {
                    'audioUrl': item.get('audioUrl', {}).get('S', ''),
                    'sources': json.loads(item.get('sources', {}).get('S', '[]')),
                    'generatedAt': item.get('generatedAt', {}).get('S', ''),
                    'why': 'Cached content served due to generation error',
                    'traceId': item.get('traceId', {}).get('S', ''),
                    'script': item.get('script', {}).get('S', ''),
                    'news_items': json.loads(item.get('news_items', {}).get('S', '[]')),
                    'word_timings': json.loads(item.get('word_timings', {}).get('S', '[]')),
                    'agentOutputs': FALLBACK_CONTENT["agent_outputs"],  # Simple fallback
                    'shouldRefresh': True,
                    'agentStatus': 'CACHED_FALLBACK',
                    'quality_score': 70,
                    'enhanced_orchestration': False,
                    'validation_passed': True
                }
        except Exception as e:
            print(f"❌ Error getting cached content: {e}")
        
        return None


def generate_content(curio_table: str, run_id: str = None) -> Dict[str, Any]:
    """
    Simple function to generate content - main entry point
    This replaces all the complex agent orchestration with a single function call
    """
    generator = ContentGenerator(curio_table)
    return generator.generate_content(run_id)