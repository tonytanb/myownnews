import json
import boto3
import time
from datetime import datetime
from typing import Dict, List, Any

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
dynamodb = boto3.client('dynamodb')

class AgentOrchestrator:
    def __init__(self, curio_table: str):
        self.curio_table = curio_table
        self.agents = [
            "NEWS_FETCHER",
            "CONTENT_CURATOR", 
            "FAVORITE_SELECTOR",
            "SCRIPT_GENERATOR",
            "MEDIA_ENHANCER",
            "WEEKEND_EVENTS"
        ]
    
    def update_agent_status(self, run_id: str, agent: str, status: str, data: Dict = None):
        """Update the current agent status in DynamoDB"""
        try:
            item = {
                'pk': {'S': f'generation#{run_id}'},
                'currentAgent': {'S': agent},
                'status': {'S': status},
                'updatedAt': {'S': datetime.utcnow().isoformat()},
                'expiresAt': {'N': str(int(time.time()) + 3600)}  # 1 hour TTL
            }
            
            if data:
                item['data'] = {'S': json.dumps(data)}
            
            dynamodb.put_item(TableName=self.curio_table, Item=item)
            print(f"✅ Agent status updated: {agent} - {status}")
        except Exception as e:
            print(f"❌ Error updating agent status: {e}")
    
    def invoke_bedrock_agent(self, agent_name: str, prompt: str, context: Dict = None) -> Dict:
        """Invoke a specialized Bedrock agent"""
        try:
            # Create agent-specific prompt
            system_prompt = self.get_agent_system_prompt(agent_name)
            full_prompt = f"{system_prompt}\n\nContext: {json.dumps(context) if context else 'None'}\n\nTask: {prompt}"
            
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-haiku-20240307-v1:0',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 2000,
                    'messages': [
                        {
                            'role': 'user',
                            'content': full_prompt
                        }
                    ]
                })
            )
            
            result = json.loads(response['body'].read())
            content = result['content'][0]['text']
            
            return {
                'success': True,
                'content': content,
                'agent': agent_name,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error invoking {agent_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent': agent_name,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_agent_system_prompt(self, agent_name: str) -> str:
        """Get the specialized system prompt for each agent"""
        prompts = {
            "NEWS_FETCHER": """You are the News Fetcher Agent, specialized in gathering and filtering news for Gen Z/Millennial audiences. 
            Your role is to identify the most relevant, engaging, and trending news stories from multiple sources.
            Focus on: Technology, culture, politics that affects young adults, science breakthroughs, and viral trends.
            Return your findings as a JSON array of news items with title, summary, category, and relevance_score.""",
            
            "CONTENT_CURATOR": """You are the Content Curator Agent, expert at selecting the perfect mix of news stories.
            Your role is to choose exactly 5 stories that create a balanced, engaging briefing.
            Ensure diversity across categories and optimize for engagement. Consider the narrative flow.
            Return a JSON object with selected stories and reasoning for each choice.""",
            
            "FAVORITE_SELECTOR": """You are the Favorite Selector Agent, specialized in finding the most interesting story of the day.
            Your role is to identify content that sparks curiosity - university research, science discoveries, cultural phenomena.
            Look for "wow, that's actually really cool!" moments that people will want to share.
            Return a JSON object with the favorite story and detailed explanation of why it's fascinating.""",
            
            "SCRIPT_GENERATOR": """You are the Script Generator Agent, expert at creating engaging news scripts.
            Your role is to transform news stories into conversational, accessible content for audio delivery.
            Write in a friendly, informative tone that feels like talking to a smart friend.
            Structure: Opening → Favorite Spotlight → Story Deep Dives → Quick Hits → Closing.
            Return a JSON object with the complete script and timing estimates.""",
            
            "MEDIA_ENHANCER": """You are the Media Enhancer Agent, specialized in visual content curation.
            Your role is to find compelling images, suggest video clips, and enhance stories with visual elements.
            Focus on accessibility, engagement, and social media optimization.
            Return a JSON object with media recommendations for each story.""",
            
            "WEEKEND_EVENTS": """You are the Weekend Events Agent, expert at curating lifestyle and cultural content.
            Your role is to recommend books, movies, events, and trending cultural phenomena.
            Focus on BookTok trends, streaming releases, local events, and social media phenomena.
            Return a JSON object with weekend recommendations and cultural insights."""
        }
        
        return prompts.get(agent_name, "You are a helpful AI assistant.")
    
    async def orchestrate_agents(self, run_id: str) -> Dict:
        """Orchestrate all 6 agents to generate a complete news briefing"""
        try:
            results = {}
            
            # Agent 1: News Fetcher
            self.update_agent_status(run_id, "NEWS_FETCHER", "RUNNING")
            news_result = self.invoke_bedrock_agent(
                "NEWS_FETCHER",
                "Fetch and filter the top 15 news stories for today, focusing on Gen Z/Millennial interests. Include technology, culture, politics, science, and trending topics."
            )
            results['news_fetcher'] = news_result
            
            if not news_result['success']:
                return {'success': False, 'error': 'News fetching failed', 'results': results}
            
            # Agent 2: Content Curator
            self.update_agent_status(run_id, "CONTENT_CURATOR", "RUNNING")
            curator_result = self.invoke_bedrock_agent(
                "CONTENT_CURATOR",
                "Select the best 5 stories from the fetched news for a balanced, engaging briefing.",
                context={'news_stories': news_result['content']}
            )
            results['content_curator'] = curator_result
            
            # Agent 3: Favorite Selector
            self.update_agent_status(run_id, "FAVORITE_SELECTOR", "RUNNING")
            favorite_result = self.invoke_bedrock_agent(
                "FAVORITE_SELECTOR",
                "Choose the most fascinating story that will spark curiosity and conversation.",
                context={'selected_stories': curator_result['content']}
            )
            results['favorite_selector'] = favorite_result
            
            # Agent 4: Script Generator
            self.update_agent_status(run_id, "SCRIPT_GENERATOR", "RUNNING")
            script_result = self.invoke_bedrock_agent(
                "SCRIPT_GENERATOR",
                "Create an engaging 90-second news script with the selected stories.",
                context={
                    'stories': curator_result['content'],
                    'favorite': favorite_result['content']
                }
            )
            results['script_generator'] = script_result
            
            # Agent 5: Media Enhancer
            self.update_agent_status(run_id, "MEDIA_ENHANCER", "RUNNING")
            media_result = self.invoke_bedrock_agent(
                "MEDIA_ENHANCER",
                "Suggest compelling visual content and media enhancements for each story.",
                context={'stories': curator_result['content']}
            )
            results['media_enhancer'] = media_result
            
            # Agent 6: Weekend Events
            self.update_agent_status(run_id, "WEEKEND_EVENTS", "RUNNING")
            weekend_result = self.invoke_bedrock_agent(
                "WEEKEND_EVENTS",
                "Recommend weekend activities, books, movies, and cultural trends.",
                context={'current_stories': curator_result['content']}
            )
            results['weekend_events'] = weekend_result
            
            # Mark as completed
            self.update_agent_status(run_id, "COMPLETED", "SUCCESS", results)
            
            return {
                'success': True,
                'run_id': run_id,
                'results': results,
                'completed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.update_agent_status(run_id, "ERROR", "FAILED", {'error': str(e)})
            return {
                'success': False,
                'error': str(e),
                'run_id': run_id,
                'results': results
            }