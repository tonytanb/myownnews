#!/usr/bin/env python3
"""
Bedrock Multi-Agent Setup Script
Creates all 6 specialized Bedrock agents for Curio News with proper IAM roles and configurations.
"""

import boto3
import json
import time
import sys
from typing import Dict, List, Optional
from botocore.exceptions import ClientError

class BedrockAgentSetup:
    def __init__(self, region: str = 'us-east-1'):
        """Initialize AWS clients for Bedrock agent setup."""
        self.region = region
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=region)
        self.iam = boto3.client('iam', region_name=region)
        self.ssm = boto3.client('ssm', region_name=region)
        self.sts = boto3.client('sts', region_name=region)
        
        # Get account ID for IAM role ARNs
        self.account_id = self.sts.get_caller_identity()['Account']
        
        self.agent_configs = self._define_agent_configs()
        self.created_agents = {}
        
    def _define_agent_configs(self) -> Dict:
        """Define all 6 Bedrock agent configurations with instructions."""
        return {
            'content_curator': {
                'name': 'curio-news-content-curator',
                'description': 'Discovers, filters, and curates the most relevant news stories for Gen Z and Millennial audiences',
                'model_id': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'enable_multi_agent': True,
                'instructions': '''You are the Content Curator Agent for Curio News. Your role is to analyze news stories and select the most relevant, high-quality content for a Gen Z and Millennial audience.

RESPONSIBILITIES:
1. Evaluate news stories for relevance, quality, and credibility
2. Filter out low-quality, duplicate, or unreliable content
3. Score each story based on social impact and audience appeal
4. Prioritize stories that benefit communities and drive positive change

SCORING CRITERIA:
- Social Impact: +5 points (community benefit, social justice, environmental progress)
- Scientific Breakthroughs: +4 points (medical advances, research discoveries)
- Educational Value: +3 points (learning opportunities, skill development)
- Cultural Significance: +3 points (arts, diversity, representation)
- Financial/Market News: -2 points (limited social impact)

OUTPUT FORMAT:
Return a JSON array of curated stories with scores:
{
  "curated_stories": [
    {
      "title": "Story title",
      "summary": "Brief summary",
      "category": "Category",
      "source": "Source name",
      "curator_score": 8.5,
      "social_impact_areas": ["community", "health"]
    }
  ],
  "total_analyzed": 15,
  "total_curated": 7
}'''
            },
            'social_impact_analyzer': {
                'name': 'curio-news-social-impact-analyzer',
                'description': 'Analyzes stories for social relevance and community benefit with focus on Gen Z/Millennial priorities',
                'model_id': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'enable_multi_agent': True,
                'instructions': '''You are the Social Impact Analyzer for Curio News. Your role is to evaluate news stories for their potential to benefit communities and resonate with socially-conscious younger generations.

RESPONSIBILITIES:
1. Identify stories with high social impact and community benefit
2. Analyze generational appeal (Gen Z and Millennial priorities)
3. Detect social themes: justice, environment, health, education, culture
4. Score stories based on their potential to inspire positive action

SOCIAL IMPACT CATEGORIES:
- Community Impact: Local initiatives, neighborhood improvements
- Environmental Progress: Climate action, sustainability, conservation
- Health Advancement: Medical breakthroughs, mental health, wellness
- Social Justice: Equality, diversity, human rights
- Education Innovation: Learning access, skill development
- Cultural Significance: Arts, representation, heritage

GENERATIONAL PRIORITIES (Gen Z/Millennial):
HIGH PRIORITY: Climate change, mental health, social justice, diversity, sustainability
MEDIUM PRIORITY: Technology innovation, education access, cultural trends
LOW PRIORITY: Stock markets, corporate earnings, traditional finance

OUTPUT FORMAT:
{
  "high_impact_stories": [
    {
      "title": "Story title",
      "impact_score": 9.2,
      "impact_areas": ["environment", "community"],
      "generational_appeal": 8.5,
      "reasoning": "Why this story matters to younger generations"
    }
  ],
  "social_themes": {
    "community_impact": 3,
    "environmental_progress": 5,
    "health_advancement": 2
  },
  "overall_generational_appeal": 7.8
}'''
            },
            'story_selector': {
                'name': 'curio-news-story-selector',
                'description': 'Selects the most compelling favorite story based on social impact and generational appeal',
                'model_id': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'enable_multi_agent': True,
                'instructions': '''You are the Story Selector Agent for Curio News. Your role is to choose the single most impactful and engaging story from the curated news list.

RESPONSIBILITIES:
1. Review curated stories and their social impact scores
2. Select the story with the highest combination of social impact and audience appeal
3. Generate compelling reasoning that explains the social benefit
4. Ensure the selected story aligns with Gen Z/Millennial values

SELECTION CRITERIA (in priority order):
1. Social Impact Score (40%): Community benefit, positive change
2. Generational Appeal (30%): Relevance to younger audiences
3. Curiosity Factor (20%): Ability to spark interest and conversation
4. Actionability (10%): Potential to inspire positive action

AVOID:
- Stories focused solely on financial markets or stock prices
- Corporate earnings reports without social impact
- Political drama without policy substance
- Celebrity gossip without cultural significance

OUTPUT FORMAT:
{
  "favorite_story": {
    "title": "Selected story title",
    "summary": "Story summary",
    "category": "Category",
    "source": "Source",
    "image": "Image URL",
    "reasoning": "🤝 Selected as today's most socially impactful story from X articles. This story represents the kind of positive change and community progress that Gen Z and Millennials care about most.",
    "social_impact_score": 9.5,
    "generational_appeal": 8.8
  }
}'''
            },
            'script_writer': {
                'name': 'curio-news-script-writer',
                'description': 'Creates engaging, conversational audio scripts for Gen Z and Millennial audiences',
                'model_id': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'enable_multi_agent': True,
                'instructions': '''You are the Script Writer Agent for Curio News. Your role is to transform curated news stories into engaging, conversational audio scripts for a Gen Z and Millennial audience.

RESPONSIBILITIES:
1. Write natural, conversational scripts (250-300 words)
2. Emphasize social impact and community benefits
3. Use warm, friendly tone that resonates with younger audiences
4. Create smooth transitions between stories
5. Open with energy and close with inspiration

SCRIPT STRUCTURE:
1. Opening Hook (20 words): Warm greeting + today's theme
2. Featured Story (100 words): Deep dive on the favorite story with social impact focus
3. Additional Stories (100 words): Brief coverage of 2-3 other impactful stories
4. Closing (30 words): Inspirational message + call to stay engaged

TONE GUIDELINES:
- Conversational and friendly (like talking to a friend)
- Optimistic and solution-focused
- Socially aware and empathetic
- Curious and engaging
- Avoid: Corporate jargon, overly formal language, doom-and-gloom

LANGUAGE STYLE:
- Use "we" and "our" to create community
- Emphasize positive change and human progress
- Highlight how stories benefit communities
- Connect stories to shared values

OUTPUT FORMAT:
{
  "script": "Full audio script text (250-300 words)",
  "word_count": 275,
  "estimated_duration_seconds": 110,
  "tone": "conversational, optimistic",
  "key_themes": ["community", "progress", "hope"]
}'''
            },
            'entertainment_curator': {
                'name': 'curio-news-entertainment-curator',
                'description': 'Curates weekend entertainment recommendations with social themes and cultural significance',
                'model_id': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'enable_multi_agent': True,
                'instructions': '''You are the Entertainment Curator Agent for Curio News. Your role is to recommend movies, TV shows, theater, and cultural events that align with current news themes and social consciousness.

RESPONSIBILITIES:
1. Recommend entertainment with social themes and cultural significance
2. Connect recommendations to current news themes
3. Ensure diverse, inclusive representation in recommendations
4. Provide context on why each recommendation matters

RECOMMENDATION CATEGORIES:
1. Top Movies: Films addressing social issues, diverse perspectives
2. Must-Watch Series: TV shows with cultural impact and representation
3. Theater & Plays: Live performances with social themes
4. Cultural Events: Exhibitions, festivals, community gatherings

SELECTION CRITERIA:
- Social Relevance: Addresses important social issues
- Cultural Significance: Represents diverse voices and perspectives
- Critical Acclaim: Well-reviewed and respected
- Accessibility: Available on popular streaming platforms
- Timeliness: Recent releases or currently relevant

OUTPUT FORMAT:
{
  "entertainment_recommendations": {
    "top_movies": [
      {
        "title": "Movie Title",
        "genre": "Documentary/Drama",
        "rating": "8.5/10",
        "platform": "Netflix",
        "description": "Why this movie matters socially",
        "social_themes": ["environment", "justice"],
        "release_year": 2024
      }
    ],
    "must_watch_series": [...],
    "theater_plays": [...]
  },
  "cultural_insights": {
    "trending_themes": ["climate action", "social justice"],
    "why_it_matters": "Connection to current events"
  }
}'''
            },
            'media_enhancer': {
                'name': 'curio-news-media-enhancer',
                'description': 'Optimizes visual content and social media presentation with accessibility features',
                'model_id': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'enable_multi_agent': True,
                'instructions': '''You are the Media Enhancement Agent for Curio News. Your role is to optimize visual content, generate accessibility features, and prepare content for social media sharing.

RESPONSIBILITIES:
1. Generate descriptive alt text for all images (accessibility)
2. Create social media hashtags aligned with story themes
3. Optimize image selection for visual storytelling
4. Ensure brand consistency and visual appeal

ENHANCEMENT AREAS:
1. Accessibility: Alt text, image descriptions, contrast checks
2. Social Media: Hashtags, sharing formats, engagement optimization
3. Visual Hierarchy: Layout recommendations, image placement
4. Brand Consistency: Color schemes, typography, style guidelines

ACCESSIBILITY STANDARDS:
- Alt text: Descriptive, concise (125 characters max)
- Image descriptions: Context and key visual elements
- Color contrast: WCAG AA compliance
- Text readability: Clear, legible fonts

OUTPUT FORMAT:
{
  "media_enhancements": {
    "stories": [
      {
        "title": "Story title",
        "media_recommendations": {
          "images": [
            {
              "url": "Image URL",
              "alt_text": "Descriptive alt text for accessibility"
            }
          ],
          "social_media_optimization": {
            "hashtags": ["#SocialImpact", "#CurioNews", "#Community"],
            "suggested_caption": "Engaging social media caption"
          }
        }
      }
    ]
  },
  "accessibility_score": 95,
  "brand_compliance": true
}'''
            }
        }
    
    def create_agent_iam_role(self, agent_key: str) -> str:
        """Create IAM role for a Bedrock agent with appropriate permissions."""
        role_name = f"CurioNewsBedrockAgent-{agent_key.replace('_', '-')}"
        
        # Trust policy for Bedrock service
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": self.account_id
                        },
                        "ArnLike": {
                            "aws:SourceArn": f"arn:aws:bedrock:{self.region}:{self.account_id}:agent/*"
                        }
                    }
                }
            ]
        }
        
        # Permissions policy for the agent
        permissions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": f"arn:aws:logs:{self.region}:{self.account_id}:log-group:/aws/bedrock/agents/*"
                }
            ]
        }
        
        try:
            # Check if role already exists
            try:
                response = self.iam.get_role(RoleName=role_name)
                role_arn = response['Role']['Arn']
                print(f"✓ IAM role already exists: {role_name}")
                return role_arn
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchEntity':
                    raise
            
            # Create the role
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"IAM role for Curio News Bedrock Agent: {agent_key}",
                Tags=[
                    {'Key': 'Project', 'Value': 'CurioNews'},
                    {'Key': 'Component', 'Value': 'BedrockAgent'},
                    {'Key': 'AgentType', 'Value': agent_key}
                ]
            )
            role_arn = response['Role']['Arn']
            
            # Attach inline policy
            self.iam.put_role_policy(
                RoleName=role_name,
                PolicyName=f"{role_name}-permissions",
                PolicyDocument=json.dumps(permissions_policy)
            )
            
            print(f"✓ Created IAM role: {role_name}")
            
            # Wait for role to be available
            time.sleep(10)
            
            return role_arn
            
        except ClientError as e:
            print(f"✗ Error creating IAM role for {agent_key}: {e}")
            raise

    def create_bedrock_agent(self, agent_key: str, config: Dict) -> Dict:
        """Create a Bedrock agent with the specified configuration."""
        try:
            # Create IAM role first
            role_arn = self.create_agent_iam_role(agent_key)
            
            # Check if agent already exists
            try:
                agents = self.bedrock_agent.list_agents()
                for agent in agents.get('agentSummaries', []):
                    if agent['agentName'] == config['name']:
                        print(f"✓ Agent already exists: {config['name']}")
                        return {
                            'agent_id': agent['agentId'],
                            'agent_name': config['name'],
                            'agent_arn': agent['agentArn'],
                            'status': 'EXISTING'
                        }
            except Exception as e:
                print(f"Warning: Could not check existing agents: {e}")
            
            # Create the agent
            print(f"Creating agent: {config['name']}...")
            
            create_params = {
                'agentName': config['name'],
                'agentResourceRoleArn': role_arn,
                'description': config['description'],
                'foundationModel': config['model_id'],
                'instruction': config['instructions'],
                'idleSessionTTLInSeconds': 600,
                'tags': {
                    'Project': 'CurioNews',
                    'Environment': 'Production',
                    'AgentType': agent_key
                }
            }
            
            # Add multi-agent collaboration settings if enabled
            if config.get('enable_multi_agent', False):
                create_params['orchestrationType'] = 'DEFAULT'  # Use DEFAULT for multi-agent collaboration
            
            response = self.bedrock_agent.create_agent(**create_params)
            
            agent_id = response['agent']['agentId']
            agent_arn = response['agent']['agentArn']
            
            print(f"✓ Created agent: {config['name']} (ID: {agent_id})")
            
            return {
                'agent_id': agent_id,
                'agent_name': config['name'],
                'agent_arn': agent_arn,
                'status': 'CREATED'
            }
            
        except ClientError as e:
            print(f"✗ Error creating agent {config['name']}: {e}")
            raise
    
    def prepare_agent(self, agent_id: str, agent_name: str) -> str:
        """Prepare the agent (create a working draft)."""
        try:
            print(f"Preparing agent: {agent_name}...")
            
            response = self.bedrock_agent.prepare_agent(agentId=agent_id)
            
            # Wait for preparation to complete
            max_attempts = 30
            for attempt in range(max_attempts):
                agent_response = self.bedrock_agent.get_agent(agentId=agent_id)
                status = agent_response['agent']['agentStatus']
                
                if status == 'PREPARED':
                    print(f"✓ Agent prepared: {agent_name}")
                    return 'PREPARED'
                elif status == 'FAILED':
                    raise Exception(f"Agent preparation failed: {agent_name}")
                
                time.sleep(2)
            
            raise Exception(f"Agent preparation timeout: {agent_name}")
            
        except ClientError as e:
            print(f"✗ Error preparing agent {agent_name}: {e}")
            raise
    
    def create_agent_alias(self, agent_id: str, agent_name: str) -> str:
        """Create a LIVE alias for the agent."""
        try:
            alias_name = 'LIVE'
            
            # Check if alias already exists
            try:
                aliases = self.bedrock_agent.list_agent_aliases(agentId=agent_id)
                for alias in aliases.get('agentAliasSummaries', []):
                    if alias['agentAliasName'] == alias_name:
                        print(f"✓ Alias already exists: {alias_name} for {agent_name}")
                        return alias['agentAliasId']
            except Exception as e:
                print(f"Warning: Could not check existing aliases: {e}")
            
            print(f"Creating alias '{alias_name}' for agent: {agent_name}...")
            
            response = self.bedrock_agent.create_agent_alias(
                agentId=agent_id,
                agentAliasName=alias_name,
                description=f"Production alias for {agent_name}",
                tags={
                    'Environment': 'Production',
                    'Project': 'CurioNews'
                }
            )
            
            alias_id = response['agentAlias']['agentAliasId']
            
            # Wait for alias to be ready
            max_attempts = 30
            for attempt in range(max_attempts):
                alias_response = self.bedrock_agent.get_agent_alias(
                    agentId=agent_id,
                    agentAliasId=alias_id
                )
                status = alias_response['agentAlias']['agentAliasStatus']
                
                if status == 'PREPARED':
                    print(f"✓ Alias created: {alias_name} (ID: {alias_id})")
                    return alias_id
                elif status == 'FAILED':
                    raise Exception(f"Alias creation failed for {agent_name}")
                
                time.sleep(2)
            
            raise Exception(f"Alias creation timeout for {agent_name}")
            
        except ClientError as e:
            print(f"✗ Error creating alias for {agent_name}: {e}")
            raise

    def store_agent_ids_in_parameter_store(self):
        """Store all agent IDs and alias IDs in AWS Systems Manager Parameter Store."""
        try:
            print("\nStoring agent IDs in Parameter Store...")
            
            for agent_key, agent_info in self.created_agents.items():
                # Store agent ID
                param_name = f"/curio-news/bedrock-agents/{agent_key}/agent-id"
                try:
                    # Try to create with tags first
                    self.ssm.put_parameter(
                        Name=param_name,
                        Value=agent_info['agent_id'],
                        Type='String',
                        Description=f"Bedrock Agent ID for {agent_info['agent_name']}",
                        Tags=[
                            {'Key': 'Project', 'Value': 'CurioNews'},
                            {'Key': 'Component', 'Value': 'BedrockAgent'}
                        ]
                    )
                except ClientError as e:
                    if 'ParameterAlreadyExists' in str(e):
                        # Parameter exists, update without tags
                        self.ssm.put_parameter(
                            Name=param_name,
                            Value=agent_info['agent_id'],
                            Type='String',
                            Description=f"Bedrock Agent ID for {agent_info['agent_name']}",
                            Overwrite=True
                        )
                    else:
                        raise
                print(f"✓ Stored parameter: {param_name}")
                
                # Store alias ID
                if 'alias_id' in agent_info:
                    alias_param_name = f"/curio-news/bedrock-agents/{agent_key}/alias-id"
                    try:
                        # Try to create with tags first
                        self.ssm.put_parameter(
                            Name=alias_param_name,
                            Value=agent_info['alias_id'],
                            Type='String',
                            Description=f"Bedrock Agent Alias ID for {agent_info['agent_name']}",
                            Tags=[
                                {'Key': 'Project', 'Value': 'CurioNews'},
                                {'Key': 'Component', 'Value': 'BedrockAgent'}
                            ]
                        )
                    except ClientError as e:
                        if 'ParameterAlreadyExists' in str(e):
                            # Parameter exists, update without tags
                            self.ssm.put_parameter(
                                Name=alias_param_name,
                                Value=agent_info['alias_id'],
                                Type='String',
                                Description=f"Bedrock Agent Alias ID for {agent_info['agent_name']}",
                                Overwrite=True
                            )
                        else:
                            raise
                    print(f"✓ Stored parameter: {alias_param_name}")
            
            # Store a consolidated JSON with all agent info
            all_agents_param = "/curio-news/bedrock-agents/all-agents"
            all_agents_data = {
                agent_key: {
                    'agent_id': info['agent_id'],
                    'agent_name': info['agent_name'],
                    'alias_id': info.get('alias_id', ''),
                    'status': info['status']
                }
                for agent_key, info in self.created_agents.items()
            }
            
            try:
                # Try to create with tags first
                self.ssm.put_parameter(
                    Name=all_agents_param,
                    Value=json.dumps(all_agents_data),
                    Type='String',
                    Description='All Curio News Bedrock Agent IDs and metadata',
                    Tags=[
                        {'Key': 'Project', 'Value': 'CurioNews'},
                        {'Key': 'Component', 'Value': 'BedrockAgent'}
                    ]
                )
            except ClientError as e:
                if 'ParameterAlreadyExists' in str(e):
                    # Parameter exists, update without tags
                    self.ssm.put_parameter(
                        Name=all_agents_param,
                        Value=json.dumps(all_agents_data),
                        Type='String',
                        Description='All Curio News Bedrock Agent IDs and metadata',
                        Overwrite=True
                    )
                else:
                    raise
            print(f"✓ Stored consolidated parameter: {all_agents_param}")
            
        except ClientError as e:
            print(f"✗ Error storing parameters: {e}")
            raise
    
    def validate_agents(self) -> bool:
        """Validate that all agents were created successfully and are accessible."""
        print("\n" + "="*60)
        print("VALIDATING AGENT CREATION")
        print("="*60)
        
        all_valid = True
        
        for agent_key, agent_info in self.created_agents.items():
            try:
                # Validate agent exists and is accessible
                response = self.bedrock_agent.get_agent(agentId=agent_info['agent_id'])
                agent_status = response['agent']['agentStatus']
                
                # Validate alias exists
                if 'alias_id' in agent_info:
                    alias_response = self.bedrock_agent.get_agent_alias(
                        agentId=agent_info['agent_id'],
                        agentAliasId=agent_info['alias_id']
                    )
                    alias_status = alias_response['agentAlias']['agentAliasStatus']
                else:
                    alias_status = 'NOT_CREATED'
                
                # Check if everything is ready
                if agent_status == 'PREPARED' and alias_status == 'PREPARED':
                    print(f"✓ {agent_info['agent_name']}: READY")
                    print(f"  Agent ID: {agent_info['agent_id']}")
                    print(f"  Alias ID: {agent_info.get('alias_id', 'N/A')}")
                else:
                    print(f"⚠ {agent_info['agent_name']}: NOT READY")
                    print(f"  Agent Status: {agent_status}")
                    print(f"  Alias Status: {alias_status}")
                    all_valid = False
                    
            except ClientError as e:
                print(f"✗ {agent_info['agent_name']}: VALIDATION FAILED")
                print(f"  Error: {e}")
                all_valid = False
        
        return all_valid
    
    def setup_all_agents(self):
        """Main method to set up all Bedrock agents."""
        print("="*60)
        print("CURIO NEWS BEDROCK MULTI-AGENT SETUP")
        print("="*60)
        print(f"Region: {self.region}")
        print(f"Account: {self.account_id}")
        print(f"Agents to create: {len(self.agent_configs)}")
        print("="*60)
        
        # Step 1: Create all agents
        print("\nSTEP 1: Creating Bedrock Agents")
        print("-"*60)
        for agent_key, config in self.agent_configs.items():
            try:
                agent_info = self.create_bedrock_agent(agent_key, config)
                self.created_agents[agent_key] = agent_info
            except Exception as e:
                print(f"Failed to create agent {agent_key}: {e}")
                sys.exit(1)
        
        # Step 2: Prepare all agents
        print("\nSTEP 2: Preparing Agents")
        print("-"*60)
        for agent_key, agent_info in self.created_agents.items():
            if agent_info['status'] == 'CREATED':
                try:
                    self.prepare_agent(agent_info['agent_id'], agent_info['agent_name'])
                except Exception as e:
                    print(f"Failed to prepare agent {agent_key}: {e}")
                    sys.exit(1)
        
        # Step 3: Create aliases
        print("\nSTEP 3: Creating Production Aliases")
        print("-"*60)
        for agent_key, agent_info in self.created_agents.items():
            try:
                alias_id = self.create_agent_alias(agent_info['agent_id'], agent_info['agent_name'])
                self.created_agents[agent_key]['alias_id'] = alias_id
            except Exception as e:
                print(f"Failed to create alias for agent {agent_key}: {e}")
                sys.exit(1)
        
        # Step 4: Store in Parameter Store
        print("\nSTEP 4: Storing Agent IDs in Parameter Store")
        print("-"*60)
        try:
            self.store_agent_ids_in_parameter_store()
        except Exception as e:
            print(f"Failed to store parameters: {e}")
            sys.exit(1)
        
        # Step 5: Validate
        print("\nSTEP 5: Validating Agent Setup")
        print("-"*60)
        if self.validate_agents():
            print("\n" + "="*60)
            print("✓ ALL AGENTS CREATED SUCCESSFULLY!")
            print("="*60)
            print("\nAgent Summary:")
            for agent_key, agent_info in self.created_agents.items():
                print(f"\n{agent_info['agent_name']}:")
                print(f"  Key: {agent_key}")
                print(f"  Agent ID: {agent_info['agent_id']}")
                print(f"  Alias ID: {agent_info.get('alias_id', 'N/A')}")
            
            print("\n" + "="*60)
            print("Next Steps:")
            print("1. Verify agents in AWS Bedrock Console")
            print("2. Update Lambda environment variables with agent IDs")
            print("3. Deploy the Bedrock orchestrator Lambda function")
            print("4. Test the multi-agent pipeline")
            print("="*60)
            return True
        else:
            print("\n" + "="*60)
            print("✗ AGENT VALIDATION FAILED")
            print("="*60)
            print("Please check the errors above and retry.")
            return False


def main():
    """Main entry point for the setup script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Set up Bedrock Multi-Agent Architecture for Curio News'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region for Bedrock agents (default: us-east-1)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate existing agents without creating new ones'
    )
    
    args = parser.parse_args()
    
    try:
        setup = BedrockAgentSetup(region=args.region)
        
        if args.validate_only:
            # Load existing agents from Parameter Store
            try:
                response = setup.ssm.get_parameter(
                    Name='/curio-news/bedrock-agents/all-agents'
                )
                setup.created_agents = json.loads(response['Parameter']['Value'])
                setup.validate_agents()
            except ClientError as e:
                print(f"Error loading agents from Parameter Store: {e}")
                sys.exit(1)
        else:
            # Full setup
            success = setup.setup_all_agents()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
